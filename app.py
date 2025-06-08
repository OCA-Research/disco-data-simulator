import pandas as pd
import numpy as np
import gradio as gr
import os

np.random.seed(42)

def generate_and_save_synthetic_data(num_customers=5000, num_months=12, tampering_rate=0.015, filename='simulated_disco_data.csv'):
    data = []
    customer_ids = [f'CUST_{i:05d}' for i in range(num_customers)]
    
    tampering_customers = np.random.choice(
        customer_ids,
        size=int(num_customers * tampering_rate),
        replace=False
    )

    for cust_id in customer_ids:
        base_consumption = np.random.uniform(50, 500)
        std_dev_consumption = base_consumption * 0.05 + np.random.uniform(5, 20)
        
        payment_history = np.random.choice(['On-time', 'Late', 'Missed'], p=[0.7, 0.2, 0.1])
        customer_category = np.random.choice(['Residential', 'Commercial'], p=[0.8, 0.2])

        is_tampering_customer = cust_id in tampering_customers
        
        tamper_duration = np.random.randint(2, 6) if is_tampering_customer else 0
        tamper_start_month = np.random.randint(3, num_months - tamper_duration + 1) if is_tampering_customer else -1

        for month in range(1, num_months + 1):
            consumption = max(0, np.random.normal(base_consumption, std_dev_consumption))
            billed_amount = consumption * np.random.uniform(20, 30)

            is_tampering_month = 0
            if is_tampering_customer and month >= tamper_start_month and month < tamper_start_month + tamper_duration:
                reduction_factor = np.random.uniform(0.1, 0.4)
                consumption *= reduction_factor
                billed_amount = consumption * np.random.uniform(20, 30)
                if np.random.rand() < 0.1:
                    consumption = np.nan
                    billed_amount = np.nan
                is_tampering_month = 1

            data.append({
                'customer_id': cust_id,
                'month': month,
                'consumption_kwh': consumption,
                'billed_amount_ngn': billed_amount,
                'payment_history': payment_history,
                'customer_category': customer_category,
                'is_tampering_month': is_tampering_month,
                'is_tampering_customer': int(is_tampering_customer)
            })

    df = pd.DataFrame(data)

    for col in ['consumption_kwh', 'billed_amount_ngn']:
        mask = np.random.rand(len(df)) < 0.005
        df.loc[mask & (df['is_tampering_month'] == 0), col] = np.nan
    
    df = df.sort_values(by=['customer_id', 'month']).reset_index(drop=True)

    df.to_csv(filename, index=False)
    return filename

def run_simulator(num_customers, num_months, tampering_rate):
    filename = generate_and_save_synthetic_data(num_customers, num_months, tampering_rate)
    return filename

demo = gr.Interface(
    fn=run_simulator,
    inputs=[
        gr.Number(label="Number of Customers", value=5000),
        gr.Number(label="Number of Months", value=12),
        gr.Slider(0.0, 0.2, value=0.015, step=0.005, label="Tampering Rate")
    ],
    outputs=gr.File(label="Download CSV"),
    title="DISCO Data Simulator",
    description="Generate synthetic electricity meter data for customers."
)

demo.launch()
