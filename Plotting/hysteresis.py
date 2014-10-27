__author__ = 'mike'

def vigin_branch(ax, hysteresis_obj, norm_factor=[1, 1],
              plt_idx=0,
              **plt_opt):
    """
    Plots the virgin branch of a hysteresis
    """
    ax.plot(hysteresis_obj.virgin['field'] / norm_factor[0],
            hysteresis_obj.virgin['mag'] / norm_factor[1],
            **plt_opt)
    
    
def up_field_branch(ax, hysteresis_obj, norm_factor=[1, 1],
              plt_idx=0,
              **plt_opt):
    """
    Plots the up_field branch of a hysteresis
    """
    ax.plot(hysteresis_obj.up_field['field'] / norm_factor[0],
            hysteresis_obj.up_field['mag'] / norm_factor[1],
            **plt_opt)
    
def down_field_branch(ax, hysteresis_obj, norm_factor=[1, 1],
              plt_idx=0,
              **plt_opt):
    """
    Plots the down_field branch of a hysteresis
    """
    ax.plot(hysteresis_obj.down_field['field'] / norm_factor[0],
            hysteresis_obj.down_field['mag'] / norm_factor[1],
            **plt_opt)