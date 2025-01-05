import pyWitness

def test_test1_load() :
     import pyWitness
     dr = pyWitness.DataRaw("../data/tutorial/test1.csv")
     assert len(dr.data) == 890, "test_tutorialCode1 wrong number of participants"

