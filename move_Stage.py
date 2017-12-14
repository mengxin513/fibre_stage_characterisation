import sys
import openflexure_stage

if __name__ == "__main__":
    try:
        x = int(sys.argv[1])
        y = int(sys.argv[2])
        z = int(sys.argv[3])
    except:
        print "usage: {} <x> <y> <z>".format(sys.argv[0])
    with openflexure_stage.OpenFlexureStage('COM3') as stage:
        stage.move_rel([x,y,z])
        