from runParameters import runParameters
from config_file_api import ComputingResources
from config_file_api import ConfigFile

# https://community.nanoporetech.com/requirements_documents/promethion-it-reqs.pdf?from=support
conversion_rate_Gbases_to_GB = 7 
#https://aws.amazon.com/blogs/hpc/benchmarking-the-oxford-nanopore-technologies-basecallers-on-aws/
fast_a100_speed_GB = float('1.63e-02')*conversion_rate_Gbases_to_GB
hac_a100_speed_GB = float('6.58e-03')*conversion_rate_Gbases_to_GB
sup_a100_speed_GB = float('1.24e-03')*conversion_rate_Gbases_to_GB

fast_v100_speed_GB = float('1.18e-02')*conversion_rate_Gbases_to_GB
hac_v100_speed_GB = float('2.01e-03')*conversion_rate_Gbases_to_GB
sup_v100_speed_GB = float('3.79e-04')*conversion_rate_Gbases_to_GB

#For 2 nodes with 2 dgx that will take 30 mins
FAST_IDEAL_SIZE_GB = 4*fast_a100_speed_GB*30*60
HAC_IDEAL_SIZE_GB = 4*hac_a100_speed_GB*30*60
SUP_IDEAL_SIZE_GB = 4*sup_a100_speed_GB*30*60


def choose_ideal_size(model):
    # Check for the keywords in the string and return the corresponding size
    #speeds = ['fast', 'hac', 'sup'] 
    #selected_speed = [model.find(speed) for speed in speeds]
    print(model)
    if 'fast' in model.lower():
        print('Target size for FAST model')
        return FAST_IDEAL_SIZE_GB
    elif 'hac' in model.lower():
        print('Target size for HAC model')
        return HAC_IDEAL_SIZE_GB
    elif 'sup' in model.lower():
        print('Target size for SUP model')
        return SUP_IDEAL_SIZE_GB
    else:
        print(f"Using default size! {model} was not recognized\n Using HAC SIZE")
        return HAC_IDEAL_SIZE_GB  

class ResourceTuning:
    '''
    This object will check if the paramters for a run are configured
    in optimal way. By default each model will arrive with a given ideal_size
    and a actual size. Based on the difference of this, it will recalculate the
    resources
    '''
    def __init__ (self, run_params, run_config):
        '''
        I need the params, and the config file in order to update
        immediatly the json file of the config
        '''
        if not isinstance(run_params, runParameters):
            raise TypeError("run_params must be an instance of runParameters")
        self.run_params = run_params
        
        if not isinstance(run_config, ConfigFile):
            raise TypeError("run_config must be an instance of ConfigFile")
        self.run_config = run_config

    def compute_resources(self):
        '''
        For the given run_params return a ComputingResourcees object
        '''
        #Standard set of resources
        if self.run_params.actual_size >= self.run_params.ideal_size:
            return ComputingResources(self.run_config, "0", ["DGX","DGX"], ["dgx001", "dgx002"],
                                                        ["10.128.2.161", "10.128.2.162"], ["64, 64"], 
                                                        ["200GB", "200GB"], ["2", "2"], ["cuda:all", "cuda:all"],
                                                        ["5", "5"])
