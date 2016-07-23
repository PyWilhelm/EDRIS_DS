from DyMat import DymolaMat
def get_time_array_from_mat(dyMat):
    if isinstance(dyMat, DymolaMat):
        return dyMat.mat['data_2'][0]


mat = DymolaMat('../Filter.mat')
print((get_time_array_from_mat(mat)))