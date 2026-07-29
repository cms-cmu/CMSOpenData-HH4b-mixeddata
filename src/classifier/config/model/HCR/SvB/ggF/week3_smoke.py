from __future__ import annotations

from .baseline import Train as BaselineTrain, Eval as BaselineEval


class Train(BaselineTrain):
    model = "SvB_ggF-week3-smoke"

    @property
    def rocs(self):
        # Disable ROC creation for the tiny Week 3 smoke test.
        # The default ROC expects both multijet and ttbar backgrounds,
        # but this small test only loads multijet + ggF.
        return []


class Eval(BaselineEval):
    model = "SvB_ggF-week3-smoke"
