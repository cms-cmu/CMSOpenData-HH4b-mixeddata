from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from functools import cached_property, reduce
from itertools import chain
from typing import TYPE_CHECKING, Iterable

from src.classifier.config.main._utils import progress_advance
from src.classifier.task import ArgParser, Dataset, converter, parse
from src.classifier.typetools import sort_frozenset
from src.utils import unique

from ..setting import IO as IOSetting

if TYPE_CHECKING:
    import pandas as pd

    from src.classifier.df.io import FromRoot, ToTensor
    from src.classifier.df.tools import DFProcessor
    from src.data_formats.root import Chunk, Friend


class LoadRoot(ABC, Dataset):
    trainable: bool = False
    evaluable: bool = False

    argparser = ArgParser()
    argparser.add_argument(
        "--files",
        action="extend",
        nargs="+",
        default=[],
        help="the paths to the ROOT files",
    )
    argparser.add_argument(
        "--filelists",
        action="extend",
        nargs="+",
        default=[],
        help=f"the paths to the filelists {parse.EMBED}",
    )
    argparser.add_argument(
        "--friends",
        action="extend",
        nargs="+",
        default=[],
        help="the paths to the json files with friend tree metadata",
    )
    argparser.add_argument(
        "--max-workers",
        type=converter.int_pos,
        default=10,
        help="the maximum number of workers to fetch metadata and load training set",
    )
    argparser.add_argument(
        "--preserve-order",
        action="store_true",
        help="keep the order of the files",
    )
    argparser.add_argument(
        "--tree",
        default="Events",
        help="the name of the TTree",
    )
    argparser.add_argument(
        "--test-files",
        type=converter.int_pos,
        default=None,
        help="limit to N files per group for quick testing",
    )
    argparser.add_argument(
        "--train-chunksize",
        type=converter.int_pos,
        default=1_000_000,
        help="the size of chunk to load training set",
        condition="trainable",
    )
    argparser.add_argument(
        "--max-root-chunks",
        type=int,
        default=0,
        help="smoke-test option: if > 0, load at most this many ROOT chunks total",
    )
    argparser.add_argument(
        "--max-eval-events",
        type=int,
        default=0,
        help="smoke-test option: if > 0, evaluate at most this many events per input file",
        condition="evaluable",
    )
    argparser.add_argument(
        "--eval-base",
        default="chunks",
        help="the base path to store the evaluation results",
        condition="evaluable",
    )
    argparser.add_argument(
        "--eval-naming",
        default=...,
        help="the rule to name friend tree files for evaluation",
        condition="evaluable",
    )

    def __init__(self):
        from src.classifier.df.io import ToTensor

        self._to_tensor = ToTensor()
        self._preprocessors: list[DFProcessor] = []
        self._postprocessors: list[DFProcessor] = []

    @property
    def to_tensor(self):
        return self._to_tensor

    @property
    def preprocessors(self):
        return self._preprocessors

    @property
    def postprocessors(self):
        return self._postprocessors

    def _parse_files(self, files: list[str], filelists: list[str]) -> list[str]:
        return unique(
            reduce(
                list.__add__,
                (parse.mapping(f, "file") or [] for f in filelists),
                files.copy(),
            )
        )

    def _parse_friends(self, friends: list[str]) -> list[Friend]:
        from src.data_formats.root import Friend

        return [Friend.from_json(parse.mapping(f, "file")) for f in friends]

    def _from_root(self):
        files = self.files
        if self.opts.test_files is not None:
            n = self.opts.test_files
            files = files[:n]
            logging.info(
                f"--test-files: limited to {len(files)} files (from {len(self.files)})"
            )
        yield self.from_root(), files

    def train(self):
        if not self.trainable:
            raise NotImplementedError(
                f"{type(self).__name__} does not support training"
            )
        loader = _load_root(
            *self._from_root(),
            max_workers=self.opts.max_workers,
            chunksize=self.opts.train_chunksize,
            tree=self.opts.tree,
            preserve_order=self.opts.preserve_order,
            max_root_chunks=getattr(self.opts, "max_root_chunks", 0),
        )
        loader.to_tensor = self.to_tensor
        loader.postprocessors = self.postprocessors
        return [loader]

    def evaluate(self):
        if not self.evaluable:
            raise NotImplementedError(
                f"{type(self).__name__} does not support evaluation"
            )
        from concurrent.futures import ProcessPoolExecutor

        from src.classifier.monitor.progress import Progress
        from src.classifier.process import pool, status
        from src.classifier.root.dataset import FriendTreeEvalDataset
        from src.data_formats.root import Chunk

        from_roots = [*self._from_root()]

        known_chunks = {}
        friends_obj = self.friends
        friend_lists = friends_obj.values() if isinstance(friends_obj, dict) else [friends_obj]

        for friend_list in friend_lists:
            for friend in friend_list:
                for chunk in getattr(friend, "_data", {}):
                    known_chunks[str(chunk.path)] = (
                        str(chunk.uuid),
                        chunk.name,
                        frozenset({"event"}),
                    )

        fetch = _fetch(
            tree=self.opts.tree,
            max_entries=getattr(self.opts, "max_eval_events", 0),
            known_chunks=known_chunks,
        )

        with Progress.new(
            total=sum(map(lambda x: len(x[1]), from_roots)),
            msg=("files", "Fetching metadata"),
        ) as progress:
            if self.opts.max_workers == 1:
                # Standalone smoke-test path:
                # Avoid ProcessPoolExecutor/forkserver hangs when using one worker.
                groups = []
                for from_root, files in from_roots:
                    group_chunks = []
                    for f in files:
                        group_chunks.append(fetch(f))
                        progress_advance(progress)
                    groups.append((from_root, group_chunks))
            else:
                with ProcessPoolExecutor(
                    max_workers=self.opts.max_workers,
                    mp_context=status.context,
                    initializer=status.initializer,
                ) as executor:
                    groups = [
                        (
                            from_root,
                            pool.map_async(
                                executor,
                                fetch,
                                files,
                                callbacks=[lambda _: progress_advance(progress)],
                                preserve_order=self.opts.preserve_order,
                            ),
                        )
                        for from_root, files in from_roots
                    ]
                    groups = [(from_root, [*files]) for from_root, files in groups]

        max_eval_events = getattr(self.opts, "max_eval_events", 0)
        if max_eval_events:
            limited_groups = []
            for from_root, chunks in groups:
                limited_chunks = []
                for chunk in chunks:
                    stop = min(max_eval_events, len(chunk))
                    if stop > 0:
                        limited_chunks.append(chunk.slice(0, stop))
                limited_groups.append((from_root, limited_chunks))
            groups = limited_groups
            logging.info(
                f"--max-eval-events: limited evaluation to {max_eval_events} events per input file"
            )

        yield FriendTreeEvalDataset(
            chunks=Chunk.common(*chain(*map(lambda x: x[1], groups))),
            load_method=_eval_root(
                *groups,
                to_tensor=self.to_tensor,
                postprocessors=self.postprocessors,
            ),
            dump_base_path=IOSetting.output / self.opts.eval_base,
            dump_naming=self.opts.eval_naming,
        )

    @cached_property
    def files(self) -> list[str]:
        return self._parse_files(self.opts.files, self.opts.filelists)

    @cached_property
    def friends(self) -> list[Friend]:
        return self._parse_friends(self.opts.friends)

    @abstractmethod
    def from_root(self) -> FromRoot: ...


class LoadGroupedRoot(LoadRoot):
    argparser = ArgParser()
    argparser.add_argument(
        "--files",
        action="append",
        nargs="+",
        metavar=("GROUPS", "PATHS"),
        default=[],
        help="comma-separated groups and paths to the ROOT file",
    )
    argparser.add_argument(
        "--filelists",
        action="append",
        nargs="+",
        metavar=("GROUPS", "PATHS"),
        default=[],
        help=f"comma-separated groups and paths to the filelist {parse.EMBED}",
    )
    argparser.add_argument(
        "--friends",
        action="append",
        nargs="+",
        metavar=("GROUPS", "PATHS"),
        default=[],
        help="comma-separated groups and paths to the json file with the friend tree metadata",
    )

    def _from_root(self):
        files = self.files
        n = self.opts.test_files
        for k in files:
            group_files = files[k]
            if n is not None:
                logging.info(
                    f"--test-files: group {k}: limited to {min(n, len(group_files))} files (from {len(group_files)})"
                )
                group_files = group_files[:n]
            yield self.from_root(k), group_files

    @cached_property
    def files(self):
        files = parse.grouped_mappings(self.opts.files, ",")
        filelists = parse.grouped_mappings(self.opts.filelists, ",")
        return {
            k: self._parse_files(files.get(k, []), filelists.get(k, []))
            for k in sort_frozenset(set(files).union(filelists))
        }

    @cached_property
    def friends(self):
        return {
            k: self._parse_friends(v)
            for k, v in parse.grouped_mappings(self.opts.friends, ",").items()
        }

    @abstractmethod
    def from_root(self, groups: frozenset[str]) -> FromRoot: ...


class _fetch:
    def __init__(self, tree: str, max_entries: int = 0, known_chunks: dict = None):
        self._tree = tree
        self._max_entries = max_entries or 0
        self._known_chunks = known_chunks or {}

    def __call__(self, path: str | Chunk):
        from uuid import UUID

        from src.data_formats.root import Chunk

        if isinstance(path, Chunk):
            return path

        path_str = str(path)
        known = self._known_chunks.get(path_str)

        if self._max_entries and known is not None:
            uuid, name, branches = known
            print(
                f"[DEBUG smoke chunk without ROOT metadata fetch] {path_str} entries=[0,{self._max_entries})",
                flush=True,
            )
            return Chunk(
                source=(path_str, UUID(uuid)),
                name=name,
                branches=branches,
                num_entries=self._max_entries,
                entry_start=0,
                entry_stop=self._max_entries,
            )

        print(f"[DEBUG opening ROOT path] {path}", flush=True)
        chunk = Chunk(source=path, name=self._tree, fetch=True)
        return chunk


class _load_root:
    to_tensor: ToTensor
    postprocessors: list[DFProcessor]

    def __init__(
        self,
        *from_root: tuple[FromRoot, list[str]],
        max_workers: int,
        chunksize: int,
        tree: str,
        preserve_order: bool,
        max_root_chunks: int = 0,
    ):
        self._from_root = from_root
        self._max_workers = max_workers
        self._chunksize = chunksize
        self._tree = tree
        self._preserve_order = preserve_order
        self._max_root_chunks = max_root_chunks or 0

    def __call__(self):
        data = self.load()
        if len(data) == 0:
            raise ValueError(
                f"Dataset loaded 0 events. Check that input ROOT files contain "
                f"the expected branches (e.g. lowpt_fourTag, lowpt_threeTag) "
                f"and that the event selection is not rejecting all events."
            )
        for p in self.postprocessors:
            data = p(data)
        return self.to_tensor.tensor(data)

    def load(self) -> pd.DataFrame:
        from concurrent.futures import ProcessPoolExecutor

        import pandas as pd

        from src.classifier.monitor.progress import Progress
        from src.classifier.process import pool, status
        from src.data_formats.root import Chunk

        # Standalone smoke-test path:
        # Avoid nested ProcessPoolExecutor/forkserver hangs when using one worker.
        if self._max_workers == 1:
            logging.info("Loading ROOT dataset in single-process mode")

            with Progress.new(
                total=sum(map(lambda x: len(x[1]), self._from_root)),
                msg=("files", "Fetching metadata"),
            ) as progress:
                chunks = []
                for _, files in self._from_root:
                    group = []
                    for f in files:
                        group.append(_fetch(tree=self._tree)(f))
                        progress_advance(progress)
                    chunks.append(group)

            with Progress.new(
                total=sum(map(len, chain(*chunks))),
                msg=("events", "Loading"),
            ) as progress:
                dfs = []
                loaded_root_chunks = 0
                max_root_chunks = self._max_root_chunks

                for i in range(len(chunks)):
                    for chunk in Chunk.balance(
                        self._chunksize,
                        *chunks[i],
                        common_branches=True,
                    ):
                        if max_root_chunks and loaded_root_chunks >= max_root_chunks:
                            logging.info(
                                "Stopping ROOT load early for smoke test:",
                                f"loaded_root_chunks={loaded_root_chunks}",
                                f"max_root_chunks={max_root_chunks}",
                            )
                            break

                        df = self._from_root[i][0](chunk)
                        loaded_root_chunks += 1
                        progress_advance(progress, len(df) if df is not None else 0)
                        dfs.append(df)

                    if max_root_chunks and loaded_root_chunks >= max_root_chunks:
                        break

            objs = list(filter(lambda x: x is not None, dfs))
            if not objs:
                df = pd.DataFrame()
                logging.info("Loaded <DataFrame>: empty (all chunks filtered or empty)")
                return df

            df = pd.concat(objs, ignore_index=True)
            logging.info(
                "Loaded <DataFrame>:",
                f"entries: {len(df)}",
                f"columns: {sorted(df.columns)}",
            )
            return df

        with ProcessPoolExecutor(
            max_workers=self._max_workers,
            mp_context=status.context,
            initializer=status.initializer,
        ) as executor:
            with Progress.new(
                total=sum(map(lambda x: len(x[1]), self._from_root)),
                msg=("files", "Fetching metadata"),
            ) as progress:
                chunks = [
                    list(
                        pool.map_async(
                            executor,
                            _fetch(tree=self._tree),
                            files,
                            callbacks=[lambda _: progress_advance(progress)],
                            preserve_order=self._preserve_order,
                        )
                    )
                    for _, files in self._from_root
                ]
            with Progress.new(
                total=sum(map(len, chain(*chunks))),
                msg=("events", "Loading"),
            ) as progress:
                dfs = [
                    *chain(
                        *(
                            pool.map_async(
                                executor,
                                self._from_root[i][0],
                                Chunk.balance(
                                    self._chunksize,
                                    *chunks[i],
                                    common_branches=True,
                                ),
                                callbacks=[
                                    lambda x: progress_advance(progress, len(x))
                                ],
                                preserve_order=self._preserve_order,
                            )
                            for i in range(len(chunks))
                        )
                    ),
                ]
        objs = list(filter(lambda x: x is not None, dfs))
        if not objs:
            df = pd.DataFrame()
            logging.info("Loaded <DataFrame>: empty (all chunks filtered or empty)")
            return df

        df = pd.concat(objs, ignore_index=True)
        logging.info(
            "Loaded <DataFrame>:",
            f"entries: {len(df)}",
            f"columns: {sorted(df.columns)}",
        )
        return df


class _eval_root:
    def __init__(
        self,
        *from_root: tuple[FromRoot, Iterable[Chunk]],
        to_tensor: ToTensor,
        postprocessors: list[DFProcessor],
    ):
        self._from_roots: list[FromRoot] = []
        self._lookup: dict[Chunk, int] = {}
        for from_root, chunks in from_root:
            idx = len(self._from_roots)
            self._from_roots.append(from_root)
            for chunk in chunks:
                self._lookup[chunk.key()] = idx
        self._postprocessors = postprocessors
        self._to_tensor = to_tensor

    def __call__(self, chunk: Chunk):
        data = self._from_roots[self._lookup[chunk]](chunk)
        for p in self._postprocessors:
            data = p(data)
        return self._to_tensor.tensor(data)
