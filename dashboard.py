import tkinter as tk
from tkinter import ttk
import threading
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import glob
import os
import BSE
import dashboardStyling
import numpy as np
from scipy import stats

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("BSE Agent Analytical Dashboard")
        self.root.geometry("1600x900")
        
        # open window maximised
        self.root.state('zoomed')

        # load styling
        dashboardStyling.setup_styles(self)

        # variables for sliders and inputs
        self.num_zip = tk.IntVar(value=10)
        self.num_zic = tk.IntVar(value=10)
        self.num_shvr = tk.IntVar(value=10)
        self.num_mom = tk.IntVar(value=10)
        self.num_przi = tk.IntVar(value=10)   
        self.num_insdr = tk.IntVar(value=10)  

        self.noise_level = tk.IntVar(value=0)
        self.latency_amount = tk.DoubleVar(value=0.0)
        self.enable_shock = tk.BooleanVar(value=False)
        self.num_runs = tk.IntVar(value=5)

        #build everything
        self.build_ui()
        
    def make_shadowed_frame(self, parent_widget, box_title="", box_side=tk.TOP, fill_dir=tk.X, should_expand=False, x_pad=0, y_pad=(0, 20)):
        # creating a fake drop shadow by putting a slightly larger dark frame behind it
        shadow_bg = tk.Frame(parent_widget, bg=self.shadow_colour, bd=0, highlightthickness=0)
        shadow_bg.pack(side=box_side, fill=fill_dir, expand=should_expand, padx=x_pad, pady=y_pad)
        
        if box_title != "":
            main_box = ttk.LabelFrame(shadow_bg, text=box_title, padding=25, style='TLabelframe')
        else:
            main_box = ttk.Frame(shadow_bg, style='Inner.TFrame', padding=25)
            

        main_box.pack(fill=tk.BOTH, expand=True, padx=(0, 6), pady=(0, 6))
        
        inside_content = ttk.Frame(main_box, style='Inner.TFrame')
        inside_content.pack(fill=tk.BOTH, expand=True)
        
        return inside_content

    def build_ui(self):
        # LEFT PANEL
        left_controls = ttk.Frame(self.root, padding=40)
        left_controls.pack(side=tk.LEFT, fill=tk.Y)

        # market composition box
        composition_box = self.make_shadowed_frame(left_controls, "Market Composition")
        dropdown_options = list(range(51))

        agent_list = [
            ("ZIP:", self.num_zip),
            ("ZIC:", self.num_zic),
            ("Shaver:", self.num_shvr),
            ("Momentum:", self.num_mom),
            ("PRZI:", self.num_przi),
            ("Insider:", self.num_insdr)
        ]

        row_count = 0
        for agent_name, agent_var in agent_list:
            label = tk.Label(composition_box, text=agent_name, bg=self.box_bg_colour, font=self.left_panel_font)
            label.grid(row=row_count, column=0, sticky="w", pady=8)
            
            combo = ttk.Combobox(composition_box, textvariable=agent_var, values=dropdown_options, state="readonly", width=12, font=self.left_panel_font)
            combo.grid(row=row_count, column=1, padx=20)
            row_count += 1



        # environmental stressors box
        stressor_box = self.make_shadowed_frame(left_controls, "Environmental Stressors")

        tk.Label(stressor_box, text="Signal Noise Level (0-10):", bg=self.box_bg_colour, font=self.left_panel_font).pack(anchor="w")
        tk.Scale(stressor_box, from_=0, to=10, resolution=1, variable=self.noise_level, orient=tk.HORIZONTAL, length=450, tickinterval=2, font=self.left_panel_font, bg=self.box_bg_colour, highlightthickness=0, bd=0).pack(fill=tk.X, pady=(0,20))

        tk.Label(stressor_box, text="Environment Freeze % (0.00-1.00):", bg=self.box_bg_colour, font=self.left_panel_font).pack(anchor="w")
        tk.Scale(stressor_box, from_=0.0, to=1.0, resolution=0.05, variable=self.latency_amount, orient=tk.HORIZONTAL, length=450, tickinterval=0.2, font=self.left_panel_font, bg=self.box_bg_colour, highlightthickness=0, bd=0).pack(fill=tk.X, pady=(0,20))
        
        ttk.Checkbutton(stressor_box, text="Enable Market Shock", variable=self.enable_shock).pack(anchor="w", pady=15)

        # execution box
        exec_box = self.make_shadowed_frame(left_controls, "Execution")

        entry_row = ttk.Frame(exec_box, style='Inner.TFrame')
        entry_row.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(entry_row, text="Number of Runs:", bg=self.box_bg_colour, font=self.left_panel_font).pack(side=tk.LEFT)
        ttk.Entry(entry_row, textvariable=self.num_runs, font=self.left_panel_font, width=12).pack(side=tk.LEFT, padx=20)

        self.btn_run_single = ttk.Button(exec_box, text="Run Single Batch Scenario", command=self.run_single_scenario)
        self.btn_run_single.pack(fill=tk.X, pady=(15, 8))

        self.btn_run_all = ttk.Button(exec_box, text="Run All Scenarios", command=self.run_all_scenarios)
        self.btn_run_all.pack(fill=tk.X, pady=8)

        self.status_label = tk.Label(exec_box, text="STATUS: Ready", font=self.big_bold_font, bg=self.box_bg_colour)
        self.status_label.pack(pady=(15, 0))




        # RIGHT PANEL
        right_panel = self.make_shadowed_frame(self.root, box_title="", box_side=tk.RIGHT, fill_dir=tk.BOTH, should_expand=True, x_pad=30, y_pad=(40, 30))

        self.notebook_main = ttk.Notebook(right_panel)
        self.notebook_main.pack(fill=tk.BOTH, expand=True)

        self.tab_single_scenario = ttk.Frame(self.notebook_main)
        self.tab_all_scenarios = ttk.Frame(self.notebook_main)
        
        self.notebook_main.add(self.tab_single_scenario, text="Single Batch Scenario")
        self.notebook_main.add(self.tab_all_scenarios, text="All Scenarios")

        # single run nested tabs
        self.single_sub_notebook = ttk.Notebook(self.tab_single_scenario)
        self.single_sub_notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.view_avg_prof = ttk.Frame(self.single_sub_notebook, style='White.TFrame')
        self.view_t_test = ttk.Frame(self.single_sub_notebook, style='White.TFrame')
        
        self.single_sub_notebook.add(self.view_avg_prof, text="Average Profit & Volatility")
        self.single_sub_notebook.add(self.view_t_test, text="Statistical Significance")

        # all runs nested tabs
        self.all_sub_notebook = ttk.Notebook(self.tab_all_scenarios)
        self.all_sub_notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.view_stress_bar_chart = ttk.Frame(self.all_sub_notebook, style='White.TFrame')
        self.view_efficiency = ttk.Frame(self.all_sub_notebook, style='White.TFrame')
        
        self.all_sub_notebook.add(self.view_stress_bar_chart, text="Stressor Impact")
        self.all_sub_notebook.add(self.view_efficiency, text="Market Efficiency")

        # placeholder text while no runs
        txt_single = "Run a single batch scenario to view visualisations"
        txt_all = "Run all scenarios to view visualisations"
        
        # initialise empty plot area for timeseries profit
        self.plot_figure = plt.figure(figsize=(12, 8))
        self.plot_canvas = FigureCanvasTkAgg(self.plot_figure, master=self.view_avg_prof)
        self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.plot_figure.text(0.5, 0.5, txt_single, ha='center', va='center', fontsize=20, color='gray')
        self.plot_canvas.draw()
        
        ttk.Label(self.view_t_test, text=txt_single, font=self.big_bold_font, foreground='gray', background='white').pack(expand=True)
        ttk.Label(self.view_stress_bar_chart, text=txt_all, font=self.big_bold_font, foreground='gray', background='white').pack(expand=True)
        ttk.Label(self.view_efficiency, text=txt_all, font=self.big_bold_font, foreground='gray', background='white').pack(expand=True)

    def run_single_scenario(self):
        # turn off button so user doesnt click twice
        self.btn_run_single.config(state=tk.DISABLED)
        total_runs = self.num_runs.get()
        self.status_label.config(text=f"STATUS: 0/{total_runs} Runs Complete", fg="blue")
        
        # delete old data files before starting
        old_csvs = glob.glob("bse_batch_*_avg_balance.csv")
        for file in old_csvs:
            os.remove(file)
            
        # run simulation in background thread
        sim_thread = threading.Thread(target=self.run_bse, daemon=True)
        sim_thread.start()

    def run_bse(self):
        runs = self.num_runs.get()
        current_noise = self.noise_level.get()
        current_latency = self.latency_amount.get()

        # build  list of buyers/sellers based on the dropdowns
        market_agents = [
            ('ZIP', self.num_zip.get()),
            ('ZIC', self.num_zic.get()),
            ('SHVR', self.num_shvr.get()),
            ('Momentum', self.num_mom.get()),
            ('PRZI', self.num_przi.get(), {'k': 4, 's_min': -1.0, 's_max': 1.0}),
            ('Insider', self.num_insdr.get())
        ]
        
        # only keep agents that have a number greater than 0
        active_agents = []
        for agent in market_agents:
            if agent[1] > 0:
                active_agents.append(agent)
                
        trader_specs = {'sellers': active_agents, 'buyers': active_agents, 'proptraders': []}
        start_sim = 0.0
        end_sim = 360.0

        # if shock is checked, split supply schedule in half
        if self.enable_shock.get() == True:
            midpoint = end_sim / 2
            supply_demands = [
                {'from': start_sim, 'to': midpoint, 'ranges': [(100, 200)], 'stepmode': 'fixed'},
                {'from': midpoint, 'to': end_sim, 'ranges': [(20, 80)], 'stepmode': 'fixed'}
            ]
        else:  
            supply_demands = [{'from': start_sim, 'to': end_sim, 'ranges': [(100, 200)], 'stepmode': 'fixed'}]
        
        order_rules = {'sup': supply_demands, 'dem': supply_demands, 'interval': 10, 'timemode': 'periodic'}
        what_to_dump = {'dump_avgbals': True, 'dump_tape': False, 'dump_blotters': False, 'dump_lobs': False, 'dump_strats': False}

        # loop through  number of trials user asked for
        for trial_num in range(1, runs + 1):
            session_name = f'bse_batch_trial{trial_num:03d}'
            
            # update ui
            self.root.after(0, self.status_label.config, {"text": f"STATUS: {trial_num}/{runs} Runs Complete"})
            
            # run bse
            BSE.market_session(session_name, start_sim, end_sim, trader_specs, order_rules, what_to_dump, False, current_noise, current_latency)

        # when finished update graphs and reset buttons
        self.root.after(0, self.draw_line_graphs)
        self.root.after(0, self.btn_run_single.config, {"state": tk.NORMAL})
        self.root.after(0, self.status_label.config, {"text": f"STATUS: Scenario complete ({runs}/{runs} Runs)", "fg": "green"})
        self.root.after(0, lambda: self.notebook_main.select(self.tab_single_scenario))
        self.root.after(0, lambda: self.single_sub_notebook.select(self.view_avg_prof))

    def read_csv_data(self, filename):
        # helper function to parse specific format BSE outputs
        rows = []
        with open(filename, 'r') as file:
            for line in file:
                items = line.split(',')
                clean_items = []
                for item in items:
                    if item.strip() != '':
                        clean_items.append(item.strip())
                        
                if len(clean_items) < 8: 
                    continue
                    
                time_point = float(clean_items[1])
                row_dict = {'time': time_point}
                
                index = 4
                while index + 3 < len(clean_items):
                    agent_type = clean_items[index]
                    profit_val = float(clean_items[index+3])
                    row_dict[agent_type] = profit_val
                    index += 4
                    
                rows.append(row_dict)
                
        return pd.DataFrame(rows)
    
    def draw_line_graphs(self):
        all_csv_files = glob.glob("bse_batch_*_avg_balance.csv")
        if len(all_csv_files) == 0:
            return
        
        # read all the data and put it in one big dataframe
        dataframes = []
        for file in all_csv_files:
            df = self.read_csv_data(file)
            dataframes.append(df)
            
        combined_data = pd.concat(dataframes)
        
        # get mean and standard dev across all trials
        average_dataframe = combined_data.groupby('time').mean().reset_index()
        std_dataframe = combined_data.groupby('time').std().reset_index() 
        
        # clear placeholder text
        for child in self.view_avg_prof.winfo_children():
            child.destroy()
            
        self.plot_figure = plt.figure(figsize=(12, 8))
        self.plot_canvas = FigureCanvasTkAgg(self.plot_figure, master=self.view_avg_prof)
        self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        #which agents are in the dataframe
        agent_names = []
        for col in average_dataframe.columns:
            if col != 'time':
                agent_names.append(col)
                
        num_of_agents = len(agent_names)
        if num_of_agents == 0: 
            return
            
        # 3 cols if more than 4 agents, else 2 cols
        if num_of_agents > 4:
            num_cols = 3
        else:
            num_cols = 2
            
        import math
        num_rows = int(math.ceil(num_of_agents / num_cols))
        
        graph_axes = self.plot_figure.subplots(num_rows, num_cols, sharex=True, sharey=True)


        if num_of_agents == 1: 
            graph_axes = [graph_axes]
        else: 
            graph_axes = graph_axes.flatten()
            
        self.plot_figure.set_layout_engine(layout='constrained', w_pad=0.2, h_pad=0.2)
            
        for i in range(len(agent_names)):
            current_agent = agent_names[i]
            current_ax = graph_axes[i]
        
            agent_colour = self.agent_colours.get(current_agent, 'black')
            
            # plot main line
            current_ax.plot(average_dataframe['time'], average_dataframe[current_agent], label=current_agent, linewidth=2.0, color=agent_colour)
            
            # fill volatility shading around it
            current_ax.fill_between(
                average_dataframe['time'], 
                average_dataframe[current_agent] - std_dataframe[current_agent], 
                average_dataframe[current_agent] + std_dataframe[current_agent], 
                color=agent_colour, 
                alpha=0.3  
            )
            
            # draw  red line if shock happened at t=180
            if self.enable_shock.get() == True:
                current_ax.axvline(x=180, color='red', linestyle='--', linewidth=2, alpha=0.7)
                
            current_ax.set_title(current_agent, fontsize=14, fontweight='bold', color=agent_colour, pad=10)
            current_ax.grid(True, alpha=0.4)
            current_ax.tick_params(axis='both', which='major', labelsize=10)

        # delete any empty graphs if the grid is not fully filled
        for empty_idx in range(num_of_agents, len(graph_axes)):
            self.plot_figure.delaxes(graph_axes[empty_idx])
            
        self.plot_figure.supxlabel('Time (Seconds)', fontsize=14, fontweight='bold')
        self.plot_figure.supylabel('Average Profit per Agent', fontsize=14, fontweight='bold')
        self.plot_figure.suptitle(f"Average Cumulative Profit & Volatility ({self.num_runs.get()} Trials)", fontsize=18, fontweight='bold')
        
        self.plot_canvas.draw()
        
        # draw t test after
        self.draw_t_test(all_csv_files, agent_names)

    def draw_t_test(self, file_list, agents):
        for child in self.view_t_test.winfo_children():
            child.destroy()

        header = ttk.Label(self.view_t_test, text="T-Test Matrix (Statistical Significance at t=360)", font=self.big_bold_font, background='white')
        header.pack(pady=20)

        # get final profits for each agent
        final_profits = {}
        for a in agents:
            final_profits[a] = []
            
        for file in file_list:
            df = self.read_csv_data(file)
            if len(df) == 0:
                continue
                
            last_row_data = df.iloc[-1]
            for a in agents:
                if a in last_row_data:
                    final_profits[a].append(last_row_data[a])
                    
        # calculate averages to rank them
        mean_profits = {}
        for a in agents:
            if len(final_profits[a]) > 0:
                mean_profits[a] = np.mean(final_profits[a])
                
        # sort agents from best to worst
        sorted_agents = sorted(mean_profits.keys(), key=lambda x: mean_profits[x], reverse=True)
        
        if len(sorted_agents) < 2:
            return

        col_names = ("Comparison", "Agent 1 (Higher)", "Agent 2 (Lower)", "P-Value", "Significant? (p < 0.05)")
        t_table = ttk.Treeview(self.view_t_test, columns=col_names, show="headings", style="Stats.Treeview")



        for c in col_names:
            t_table.heading(c, text=c)
            t_table.column(c, anchor="center", width=180)

        t_table.pack(pady=20, padx=40, fill=tk.BOTH, expand=True)

        t_table.tag_configure("sig", background="#d4edda", foreground="black", font=('Segoe UI', 16)) 
        t_table.tag_configure("notsig", background="#f8d7da", foreground="black", font=('Segoe UI', 16)) 

        # compare everyone against everyone below them
        for i in range(len(sorted_agents)):
            for j in range(i + 1, len(sorted_agents)):
                better_agent = sorted_agents[i]
                worse_agent = sorted_agents[j]
                
                data_better = final_profits[better_agent]
                data_worse = final_profits[worse_agent]
                
                # do t test and handle cases where variance is 0 or if the user only ran 1 trial
                if len(data_better) < 2 or len(data_worse) < 2 or (np.var(data_better) == 0 and np.var(data_worse) == 0): 
                    p_value = 1.0
                else: 
                    test_stat, p_value = stats.ttest_ind(data_better, data_worse, equal_var=False)
                
                if p_value < 0.05:
                    sig_text = "YES"
                    row_tag = "sig"
                else:
                    sig_text = "NO"
                    row_tag = "notsig"
                
                t_table.insert("", tk.END, values=(
                    f"Rank {i+1} vs Rank {j+1}",
                    f"{better_agent} ({mean_profits[better_agent]:.1f})", 
                    f"{worse_agent} ({mean_profits[worse_agent]:.1f})", 
                    f"{p_value:.4f}", 
                    sig_text
                ), tags=(row_tag,))

    def run_all_scenarios(self):
        # disable buttons
        self.btn_run_single.config(state=tk.DISABLED)
        self.btn_run_all.config(state=tk.DISABLED)
        total = self.num_runs.get()
        self.status_label.config(text=f"STATUS: 0/5 1. Control ({0}/{total} Runs)", fg="purple")
        
        all_scenarios_thread = threading.Thread(target=self.running_all_scenarios, daemon=True)
        all_scenarios_thread.start()

    def running_all_scenarios(self):
        runs = self.num_runs.get()

        # setup stressor values: if user left them at 0, use defaults
        user_noise = self.noise_level.get()
        if user_noise > 0:
            noise = user_noise
        else:
            noise = 8
            
        user_latency = self.latency_amount.get()
        if user_latency > 0.0:
            latency = user_latency
        else:
            latency = 0.8

        # defining the 5 specific environments
        study_environments = {
            "1. Control": {"n": 0, "l": 0.0, "s": False},
            "2. Noise Only": {"n": noise, "l": 0.0, "s": False},  
            "3. Latency Only": {"n": 0, "l": latency, "s": False}, 
            "4. Shock Only": {"n": 0, "l": 0.0, "s": True},
            "5. All Stressors": {"n": noise, "l": latency, "s": True}
        }

        # get active agents again
        market_agents = [
            ('ZIP', self.num_zip.get()),
            ('ZIC', self.num_zic.get()),
            ('SHVR', self.num_shvr.get()),
            ('Momentum', self.num_mom.get()),
            ('PRZI', self.num_przi.get(), {'k': 4, 's_min': -1.0, 's_max': 1.0}),
            ('Insider', self.num_insdr.get())
        ]
        
        active_agents = []
        for agent in market_agents:
            if agent[1] > 0:
                active_agents.append(agent)
                
        trader_specs = {'sellers': active_agents, 'buyers': active_agents, 'proptraders': []}
        start_sim = 0.0
        end_sim = 360.0

        # dictionary to store the final results of each scenario
        self.all_scens_data = {}
        total_envs = len(study_environments)
        current_env_index = 1

        for env_name, env_settings in study_environments.items():
            
            # clean up files
            old_files = glob.glob("bse_batch_*_avg_balance.csv")
            for f in old_files:
                os.remove(f)

            if env_settings["s"] == True:
                midpoint = end_sim / 2
                supply_demands = [
                    {'from': start_sim, 'to': midpoint, 'ranges': [(100, 200)], 'stepmode': 'fixed'},
                    {'from': midpoint, 'to': end_sim, 'ranges': [(20, 80)], 'stepmode': 'fixed'}
                ]
            else:
                supply_demands = [{'from': start_sim, 'to': end_sim, 'ranges': [(100, 200)], 'stepmode': 'fixed'}]

            order_rules = {'sup': supply_demands, 'dem': supply_demands, 'interval': 10, 'timemode': 'periodic'}
            what_to_dump = {'dump_avgbals': True, 'dump_tape': False, 'dump_blotters': False, 'dump_lobs': False, 'dump_strats': False}

            for trial_num in range(1, runs + 1):
                sess_name = f'bse_batch_trial{trial_num:03d}'
                
                # update status ui
                self.root.after(0, self.status_label.config, {"text": f"STATUS: {current_env_index}/{total_envs} {env_name} ({trial_num}/{runs} Runs)"})
                
                try:
                    BSE.market_session(sess_name, start_sim, end_sim, trader_specs, order_rules, what_to_dump, False, env_settings["n"], env_settings["l"])
                except Exception as e:
                    import traceback
                    print(f"BSE crashed in scenario: {env_name}")
                    traceback.print_exc()
                    return 
                    
            # processing results for this scenario
            csvs_made = glob.glob("bse_batch_*_avg_balance.csv")
            
            dfs = []
            for file in csvs_made:
                parsed_df = self.read_csv_data(file)
                dfs.append(parsed_df)
                
            if len(dfs) == 0: 
                continue
            
            big_df = pd.concat(dfs)
            mean_df = big_df.groupby('time').mean().reset_index()
            
            # we just need the last row (t=360) for the bar charts
            last_row = mean_df.iloc[-1]
            

            # save it to dictionary
            agents_found = []
            for col in mean_df.columns:
                if col != 'time':
                    agents_found.append(col)
                    
            env_results = {}
            for a in agents_found:
                if a in last_row:
                    env_results[a] = last_row[a]
                    

            self.all_scens_data[env_name] = env_results
            current_env_index += 1

        # draw charts
        self.root.after(0, self.draw_all_scens_bars)
        self.root.after(0, self.draw_efficiency_table)
        
        # turn buttons back on
        self.root.after(0, self.btn_run_single.config, {"state": tk.NORMAL})
        self.root.after(0, self.btn_run_all.config, {"state": tk.NORMAL})
        self.root.after(0, self.status_label.config, {"text": f"STATUS: {total_envs}/{total_envs} scenarios complete ({runs}/{runs} runs)", "fg": "green"})
        self.root.after(0, lambda: self.notebook_main.select(self.tab_all_scenarios))
        self.root.after(0, lambda: self.all_sub_notebook.select(self.view_stress_bar_chart))

    def draw_all_scens_bars(self):
        for child in self.view_stress_bar_chart.winfo_children():
            child.destroy()

        chart_fig = plt.figure(figsize=(12, 8))
        canvas = FigureCanvasTkAgg(chart_fig, master=self.view_stress_bar_chart)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        axes = chart_fig.add_subplot(111)
        
        scenario_names = list(self.all_scens_data.keys())
        if len(scenario_names) == 0: 
            return
            
        agent_names = list(self.all_scens_data[scenario_names[0]].keys())

        x_positions = np.arange(len(scenario_names))
        
        if len(agent_names) > 0:
            bar_width = 0.8 / len(agent_names) 
        else:
            bar_width = 0.15
            
        current_offset_multiplier = 0

        for agent in agent_names:
            agent_profits_list = []
            for sc in scenario_names:
                # get profit and default to 0 if something went wrong
                p = self.all_scens_data[sc].get(agent, 0)
                agent_profits_list.append(p)
                
            offset_val = bar_width * current_offset_multiplier
            
            agent_colour = self.agent_colours.get(agent, 'black')
            axes.bar(x_positions + offset_val, agent_profits_list, bar_width, label=agent, color=agent_colour, edgecolor='black', linewidth=1.0)
            
            current_offset_multiplier += 1

        axes.set_ylabel('Final Average Profit (t=360)', fontsize=16, fontweight='bold')
        axes.set_title('Profit Degradation Across Environmental Stressors', fontsize=20, fontweight='bold', pad=15)
        
        # centre the ticks under the grouped bars
        tick_offset = (bar_width * (len(agent_names) - 1)) / 2
        axes.set_xticks(x_positions + tick_offset)
        axes.set_xticklabels(scenario_names, fontsize=14, fontweight='bold')
        axes.tick_params(axis='y', labelsize=12)
        
        axes.legend(fontsize=12, loc='upper right', bbox_to_anchor=(1.0, 1.0))
        axes.grid(True, axis='y', alpha=0.4, linestyle='--')

        chart_fig.set_layout_engine('constrained')
        canvas.draw()

    def draw_efficiency_table(self):
        for child in self.view_efficiency.winfo_children():
            child.destroy()

        top_frame = ttk.Frame(self.view_efficiency, style='White.TFrame')
        top_frame.pack(fill=tk.X, padx=40, pady=(20, 0))
        title_label = ttk.Label(top_frame, text="Agent Efficiency Percentage (Against Insider upper bound)", font=self.big_bold_font, background='white')
        title_label.pack(pady=(0, 10))

        scenario_names = list(self.all_scens_data.keys())
        if len(scenario_names) == 0: 
            return
            
        agent_names = list(self.all_scens_data[scenario_names[0]].keys())

        # find out who the best agent in the control group was to use as the 100% baseline
        try:
            theoretical_max_profit = self.all_scens_data["1. Control"]["Insider"]
        except KeyError:
            highest = 0
            if "1. Control" in self.all_scens_data:
                for val in self.all_scens_data["1. Control"].values():
                    if val > highest:
                        highest = val
            else:
                first_scen = scenario_names[0]
                for val in self.all_scens_data[first_scen].values():
                    if val > highest:
                        highest = val
            theoretical_max_profit = highest

        if theoretical_max_profit == 0: 
            theoretical_max_profit = 1 

        column_headers = ["Agent"] + scenario_names

        efficiency_table = ttk.Treeview(top_frame, columns=column_headers, show="headings", height=len(agent_names), style="Eff.Treeview")
        
        for col_name in column_headers:
            efficiency_table.heading(col_name, text=col_name)
            if col_name == "Agent":
                col_width = 180
            else:
                col_width = 150
            efficiency_table.column(col_name, anchor="center", width=col_width)

        efficiency_table.pack(fill=tk.X, expand=False, pady=10)
        efficiency_table.tag_configure("eff_row", font=('Segoe UI', 16))

        for agent in agent_names:
            row_data = [agent]
            for sc in scenario_names:
                profit_made = self.all_scens_data[sc].get(agent, 0)
                eff_percent = (profit_made / theoretical_max_profit) * 100
                row_data.append(f"{eff_percent:.2f}%")
                
            efficiency_table.insert("", tk.END, values=row_data, tags=("eff_row",))

        # create chart underneath table
        bottom_frame = ttk.Frame(self.view_efficiency, style='White.TFrame')
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)

        bottom_fig = plt.figure(figsize=(12, 4))
        bottom_canvas = FigureCanvasTkAgg(bottom_fig, master=bottom_frame)
        bottom_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        efficiency_axes = bottom_fig.add_subplot(111)
        markers = ['o', 's', '^', 'D', 'v', 'p']
        
        for idx in range(len(agent_names)):
            agent = agent_names[idx]
            agent_efficiencies = []
            
            for sc in scenario_names:
                p = self.all_scens_data[sc].get(agent, 0)
                agent_efficiencies.append((p / theoretical_max_profit) * 100)
                
            agent_colour = self.agent_colours.get(agent, 'black')
            marker_shape = markers[idx % len(markers)]
            
            efficiency_axes.plot(scenario_names, agent_efficiencies, label=agent, linewidth=2.5, marker=marker_shape, markersize=8, color=agent_colour)

        efficiency_axes.set_ylabel('Efficiency (%)', fontsize=14, fontweight='bold')
        efficiency_axes.tick_params(axis='x', labelsize=12)
        efficiency_axes.tick_params(axis='y', labelsize=12)
        
        from matplotlib.ticker import PercentFormatter
        efficiency_axes.yaxis.set_major_formatter(PercentFormatter())

        efficiency_axes.legend(fontsize=12, loc='upper right', bbox_to_anchor=(1.0, 1.0))
        efficiency_axes.grid(True, alpha=0.4, linestyle='--')
        
        bottom_fig.set_layout_engine('constrained')
        bottom_canvas.draw()

if __name__ == "__main__":
    main_window = tk.Tk()
    app_instance = Dashboard(main_window)
    main_window.mainloop()