import matplotlib
matplotlib.use('Agg')

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import json

def generate_hammett_plot(substituents, values, y_axis_label, log_transform, sigma_type, upload_folder):
    # 读取data.xlsx
    data_file = 'Table_1.xlsx'
    df_data = pd.read_excel(data_file)
    
    # 根据用户选择来获取σp或σm
    sigma_column = 'σp' if sigma_type == 'p' else 'σm'
    sigma_values = df_data.set_index('substituent')[sigma_column].to_dict()

    def plot_hammett(x_data, y_data, subs, title, xlabel, ylabel, slope, intercept, r_squared):
        plt.figure(figsize=(10, 6))
        plt.scatter(x_data, y_data)
        for i, txt in enumerate(subs):
            plt.annotate(txt, (x_data[i], y_data[i]))
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

       
        plt.plot(x_data, slope * np.array(x_data) + intercept, color='red')

       
        equation_text = f'y = {slope:.2f}x + {intercept:.2f}\n$R^2$ = {r_squared:.4f}'
        plt.text(0.05, 0.85, equation_text, transform=plt.gca().transAxes, fontsize=12, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))

        plt.grid(True)
        plot_image_path = os.path.join(upload_folder, 'hammett_plot.png')
        plt.savefig(plot_image_path)
        plt.close()

        return plot_image_path


    sigma = [sigma_values[sub] for sub in substituents]

   
    y_data = pd.to_numeric(values, errors='coerce').tolist()
    if log_transform:
        y_data = np.log10(y_data).tolist()

    y_axis_label = f'log({y_axis_label})' if log_transform else y_axis_label

    
    sigma = pd.to_numeric(sigma, errors='coerce').tolist()

  
    X = np.array(sigma).reshape(-1, 1)
    y = np.array(y_data)
    reg = LinearRegression().fit(X, y)
    slope = reg.coef_[0]
    intercept = reg.intercept_
    r_squared = r2_score(y, reg.predict(X))

    plot_image_path = plot_hammett(sigma, y_data, substituents, 'Hammett Plot', sigma_column, y_axis_label, slope, intercept, r_squared)

  
    data_json = {
        "substituent": substituents,
        y_axis_label: values,
        sigma_column: sigma,
        "ρ": slope,
        "R²": r_squared
    }

   
    output_path = os.path.join(upload_folder, 'output.xlsx')
    df_output = pd.DataFrame({
        'question': ['provide a simple mechanistic insights based on the Hammett analysis ,just analysis and interpretation.'],
        'data': [json.dumps(data_json, ensure_ascii=False)]
    })
    df_output.to_excel(output_path, index=False)

    return plot_image_path, output_path
