import PIConnectModel as pim
import PIMVC 

if __name__ == "__main__":
    piview = PIMVC.PISlide()
    pi_parameters = {u'n_eck' : 5500, u'n_max': 9000}
    base_op = dict(t = 10, n = 5500,  RCI = 20, T = 10, SoH = 100, mode = "mot")
    pimodel = pim.PINormalModel(base_op=base_op, controller=None, edb_paths=None, 
                                pi_parameters=pi_parameters, y_max=None)
    picontroller = PIMVC.PIController(pimodel, piview)
    picontroller.save("test_new.pptx")
