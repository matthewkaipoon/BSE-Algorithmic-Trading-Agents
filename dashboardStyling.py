import tkinter as tk
from tkinter import ttk

def setup_styles(dash):
    # main colour palette for dashboard
    dash.main_bg_colour = '#E5F9FF'
    dash.box_bg_colour = '#D4F5FF' 
    dash.shadow_colour = '#9EBDC6' 
    dash.highlight_border_colour = '#29404D' # dark blue for when you click a tab
    
    dash.root.configure(bg=dash.main_bg_colour)
    
    # dictionary for agent colours
    dash.agent_colours = {
        'Insider': '#71EBA0',
        'Momentum': '#EBB071',
        'PRZI': '#C75252',
        'SHVR': '#8952C7',
        'ZIC': '#87B8E6',
        'ZIP': '#F2B6E9'
    }

    # standard fonts for the graphs and tables
    dash.standard_font = ('Segoe UI', 14)
    dash.bold_header_font = ('Segoe UI', 16, 'bold')
    dash.big_bold_font = ('Segoe UI', 18, 'bold')
    

    # fonts for left control panel
    dash.left_panel_font = ('Segoe UI', 18)
    dash.left_panel_title = ('Segoe UI', 18, 'bold')
    dash.root.option_add('*TCombobox*Listbox.font', dash.left_panel_font)

    # configure tkinter styles
    dash_style = ttk.Style()
    dash_style.theme_use('clam') 
    
    dash_style.configure('.', background=dash.main_bg_colour, font=dash.standard_font)
    dash_style.configure('TLabelframe', background=dash.box_bg_colour, borderwidth=0, relief='flat', labelanchor='n')
    dash_style.configure('TLabelframe.Label', background=dash.box_bg_colour, font=dash.left_panel_title, borderwidth=0)
    
    # generic frames
    dash_style.configure('TFrame', background=dash.main_bg_colour, borderwidth=0, relief='flat')
    dash_style.configure('Inner.TFrame', background=dash.box_bg_colour, borderwidth=0, relief='flat')
    dash_style.configure('White.TFrame', background='white', borderwidth=0, relief='flat') 
    
    # buttons and checkboxes
    dash_style.configure('TButton', font=dash.left_panel_title, padding=12)
    dash_style.configure('TCheckbutton', background=dash.box_bg_colour, indicatorsize=20, font=dash.left_panel_font)
    
    
    dash_style.map('TCombobox', 
                 fieldbackground=[('readonly', 'white')], 
                 selectbackground=[('readonly', 'white')], 
                 selectforeground=[('readonly', 'black')])
    
    # TAB STYLING
    tab_text_style = ('Segoe UI', 21, 'bold')
    dash_style.configure('TNotebook', background=dash.main_bg_colour, borderwidth=0)
    
    dash_style.configure('TNotebook.Tab', font=tab_text_style, width=26, anchor="center", 
                       background=dash.box_bg_colour, borderwidth=10, bordercolor=dash.box_bg_colour, 
                       lightcolor=dash.box_bg_colour, darkcolor=dash.box_bg_colour, relief='flat')
    
    #clicking tab
    dash_style.map('TNotebook.Tab', 
                 background=[('selected', dash.box_bg_colour)],
                 bordercolor=[('selected', dash.highlight_border_colour)],
                 lightcolor=[('selected', dash.highlight_border_colour)],
                 darkcolor=[('selected', dash.highlight_border_colour)],
                 padding=[('selected', [0, 13]), ('!selected', [0, 13])],
                 expand=[('selected', [0, 0, 0, 0]), ('!selected', [0, 0, 0, 0])]
                 )

    # data tables styling 
    dash_style.configure("Stats.Treeview", font=('Segoe UI', 16), rowheight=60)
    dash_style.configure("Stats.Treeview.Heading", font=('Segoe UI', 18, 'bold'))

    dash_style.configure("Eff.Treeview", font=('Segoe UI', 16), rowheight=50) 
    dash_style.configure("Eff.Treeview.Heading", font=('Segoe UI', 18, 'bold'))