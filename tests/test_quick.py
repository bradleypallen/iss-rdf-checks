"""Quick subsets of the check scripts, importable from checks/ (pyproject.toml
puts it on the path). Seeds and sizes are fixed; the full runs are in README."""
import pytest


def test_recovery_100_cases(log):
    import check_recovery
    st = check_recovery.run(seed=1, n_regimes=4, n_pairs=25)
    assert st['cases'] == 100
    assert st['mismatch_thm2'] == 0 and st['mismatch_prop2'] == 0
    assert st['overN_mismatch'] >= 1                 # the control fires even at this size
    log(f"check_recovery seed 1, 100 cases: {st}")


def test_exhaustive_multi_size2(log):
    import check_exhaustive
    assert check_exhaustive.main('multi', 2) == [0, 0]
    log("check_exhaustive multi, size 2: 0 mismatches")


def test_2bn_fast_small(log):
    import check_recovery_2bn_fast
    st = check_recovery_2bn_fast.run(1, n_regimes=4, n_pairs=10)
    assert st['thm2'] == 0 and st['prop2'] == 0 and st['cases'] == 40
    log(f"check_recovery_2bn_fast seed 1, 40 cases: {st}")


def test_theorem1_two_bearers(log):
    import check_theorem1
    st = check_theorem1.run(1, 2)
    assert st['violations'] == 0 and st['checked'] > 0
    log(f"check_theorem1 seed 1, 2 bearers: {st}")


def test_lemma1_vs_rdflib(log):
    pytest.importorskip('rdflib')
    import check_lemma1
    st = check_lemma1.run(1, n=300)
    assert st['mismatch'] == 0
    log(f"check_lemma1 seed 1, 300 pairs: {st}")


def test_owlrl_rdfs_small(log):
    pytest.importorskip('owlrl')
    import check_owlrl
    st = check_owlrl.run(1, False, 20)
    assert st['mismatch'] == 0 and st['cases'] == 20
    log(f"check_owlrl seed 1 rdfs, 20 cases: {st}")
