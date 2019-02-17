import matplotlib.pyplot as plt


def visualisation(file_path, x_data, y_data, data_names, title, x_label='x_axis', y_label='y_axis', width=30, height=18, fontsize=16):
    fig, ax = plt.subplots(figsize=(width, height))
    for i in range(len(y_data)):
        ax.plot(x_data, y_data[i], label=data_names[i])
    ax.legend(fontsize=fontsize)
    plt.title(title)
    ax.set_xlabel(x_label, fontsize=fontsize)
    ax.set_ylabel(y_label, fontsize=fontsize)
    plt.grid(True)
    fig.savefig(file_path)
    plt.close('all')
