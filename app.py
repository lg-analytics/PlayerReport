import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
from shiny import *
from shiny.types import ImgData
import shinyswatch
from pathlib import Path

SP = Path(__file__).parent / "ShotPercentage.xlsx"
shotpercentage = pd.read_excel(SP)
CS = Path(__file__).parent / "ShotLocation.xlsx"
chartshotlocation = pd.read_excel(CS)
a = Path(__file__).parent / "all.xlsx"
all = pd.read_excel(a)
f = Path(__file__).parent / "final.xlsx"
final = pd.read_excel(f)
adv = Path(__file__).parent / "advancedstats.xlsx"
advancedstats = pd.read_excel(adv)

player_list = shotpercentage['Player'].tolist()

app_ui = ui.page_fluid(
        shinyswatch.theme.superhero(),
        ui.tags.style(
        """
        .app-col {
            border: 1px solid white;
            border-radius: 5px;
            padding: 8px;
            margin-top: 5px;
            margin-bottom: 5px;
        }
        """
    ),
    ui.h3("NBA Player Scouting Report", class_="app-heading", align="center"),
    ui.tags.div(ui.input_select(id="Player", label="Player:", choices=player_list), align='center'),
    ui.row(ui.column(4,ui.tags.div(ui.tags.b("General Stats"),ui.tags.div(ui.output_table("general"),align="center"),align="center"),ui.tags.div(ui.tags.b("Shot Chart"),ui.tags.div(ui.output_image("shot_chart"),align="center"),align="center")),
           ui.column(4,ui.tags.div(ui.tags.b("Offensive Stat Percentile by Position"),ui.tags.div(ui.output_table("offense"),align="center"),align="center"),ui.tags.div(ui.tags.b("Defensive Stat Percentile by Position"),ui.tags.div(ui.output_table("defense"),align="center"),align="center"),ui.tags.div(ui.tags.b("Player Impact Rating"),ui.tags.div(ui.output_table("rating"),align="center"),align="center"),ui.tags.div(
                {"class": "app-col"},
                ui.tags.b("Glossary"),
                ui.tags.div(ui.p("RA FG% = Restricted Area FG%"),align="center"),
                ui.tags.div(ui.p("Paint FG% = Paint (Non-Restricted Area) FG% "),align="center"),
                ui.tags.div(ui.p(" ATB FG% = Above the Break FG% "),align="center"), 
                ui.tags.div(ui.p("CONT% = Contested Shot Percentile"),align="center"),
                ui.tags.div(ui.p("DEFL% = Deflection Percentile"),align="center"),
                ui.tags.div(ui.p("DFG% = Defensive FG Percentile"),align="center"), align="center")),ui.column(4,ui.tags.div(ui.tags.b("FG% by Location"),ui.tags.div(ui.output_table("second"),align="center"),align="center"),ui.tags.div(ui.tags.b("Percentage of Shot Location"),ui.tags.div(ui.output_image("plot"),align="center"),align="center"))))

def server(input, output, session):
    @output
    @render.image
    def shot_chart():
        try:
            from pathlib import Path
            sd = Path(__file__).parent / "ShotJSON.csv"
            shotdata = pd.read_csv(sd)
            shotdata = shotdata.reset_index(drop=True)
            player_data = shotdata[shotdata['PLAYER_NAME'] == input.Player()]
            def create_court(ax, color):

            # Short corner 3PT lines
                ax.plot([-220, -220], [0, 140], linewidth=2, color=color)
                ax.plot([220, 220], [0, 140], linewidth=2, color=color)
    
            # 3PT Arc
                ax.add_artist(mpl.patches.Arc((0, 140), 440, 315, theta1=0, theta2=180, facecolor='none', edgecolor=color, lw=2))
    
            # Lane and Key
                ax.plot([-80, -80], [0, 190], linewidth=2, color=color)
                ax.plot([80, 80], [0, 190], linewidth=2, color=color)
                ax.plot([-60, -60], [0, 190], linewidth=2, color=color)
                ax.plot([60, 60], [0, 190], linewidth=2, color=color)
                ax.plot([-80, 80], [190, 190], linewidth=2, color=color)
                ax.add_artist(mpl.patches.Circle((0, 190), 60, facecolor='none', edgecolor=color, lw=2))
    
            # Rim
                ax.add_artist(mpl.patches.Circle((0, 60), 15, facecolor='none', edgecolor=color, lw=2))
    
            # Backboard
                ax.plot([-30, 30], [40, 40], linewidth=2, color=color)
    
            # Remove ticks
                ax.set_xticks([])
                ax.set_yticks([])
    
    # Set axis limits
                ax.set_xlim(-250, 250)
                ax.set_ylim(0, 470)
    
                return ax
        
            mpl.rcParams['font.size'] = 18
            mpl.rcParams['axes.linewidth'] = 2

        # Create figure and axes
            fig = plt.figure(figsize=(4, 3.76))
            ax = fig.add_axes([0, 0, 1, 1])

        # Draw court
            ax = create_court(ax, 'black')
            ax.set_facecolor('lightgray') 
        # Plot hexbin of shots
            ax.hexbin(player_data['LOC_X'], player_data['LOC_Y'] + 60, gridsize=(30, 30), extent=(-300, 300, 0, 940), bins='log', cmap='Blues')
            image_path = 'shot_chart.png'  # Specify your desired file path and name
            plt.savefig(image_path, dpi=300, bbox_inches='tight')
    
    # Close the plot
            plt.close()
            from pathlib import Path
            img: ImgData = {"src": image_path, "width": "395px", "height": "275px"}
            return img
        except:
            pass
    
    @output
    @render.table
    def second():
        if not input.Player():
         return shotpercentage
        else:
           sp = shotpercentage[shotpercentage['Player'] == input.Player()]
           sp= sp.loc[:, ['RA FG%', 'Paint FG%', 'Mid-Range FG%', 'ATB 3P%', 'Corner 3P%']]
           return sp
    
    @output
    @render.table
    def offense():
        if not input.Player():
         return all
        else:
           offensive = all[all['PLAYER_NAME'] == input.Player()]
           offensive['POS'] = offensive['Position Group']
           offensive = offensive.loc[:, ['POS', 'AST%', 'PTS%', 'ORB%', 'TOV%', 'TS%']]
           offensive['AST%'] = offensive['AST%'].apply(lambda x: "{:.2%}".format(x))
           offensive['PTS%'] = offensive['PTS%'].apply(lambda x: "{:.2%}".format(x))
           offensive['ORB%'] = offensive['ORB%'].apply(lambda x: "{:.2%}".format(x))
           offensive['TOV%'] = offensive['TOV%'].apply(lambda x: "{:.2%}".format(x))
           offensive['TS%'] = offensive['TS%'].apply(lambda x: "{:.2%}".format(x))
           return offensive
    @output
    @render.table
    def defense():
        if not input.Player():
         return all
        else:
           defensive = all[all['PLAYER_NAME'] == input.Player()]
           defensive['POS'] = defensive['Position Group']
           defensive['CONT%'] = defensive['CONTSHOT%']
           defensive = defensive.loc[:, ['POS', 'BLK%', 'STL%', 'CONT%', 'DEFL%', 'DFG%']]
           defensive['BLK%'] = defensive['BLK%'].apply(lambda x: "{:.2%}".format(x))
           defensive['STL%'] = defensive['STL%'].apply(lambda x: "{:.2%}".format(x))
           defensive['CONT%'] = defensive['CONT%'].apply(lambda x: "{:.2%}".format(x))
           defensive['DEFL%'] = defensive['DEFL%'].apply(lambda x: "{:.2%}".format(x))
           defensive['DFG%'] = defensive['DFG%'].apply(lambda x: "{:.2%}".format(x))
           return defensive
        
    @output
    @render.table
    def general():
        try:
            if not input.Player():
                return advancedstats
            else:
                general = advancedstats[advancedstats['PLAYER_NAME'] == input.Player()]
                general['PPG'] = general['PTS']
                general['RPG'] = general['REB']
                general['APG'] = general['AST']
                general['FG%'] = general['FG_PCT'].apply(lambda x: "{:.2%}".format(x))
                general['3P%'] = general['FG3_PCT'].apply(lambda x: "{:.2%}".format(x))
                general['FT%'] = general['FT_PCT'].apply(lambda x: "{:.2%}".format(x))
                general = general.loc[:, ['PPG', 'RPG', 'APG', 'FG%', '3P%', 'FT%']]
                return general
        except:
            pass
    
    @output
    @render.table
    def rating():
        try:
            if not input.Player():
                return final
            else:
                playerimpact = final[final['PLAYER_NAME'] == input.Player()]
                playerimpact = playerimpact.loc[:, ['League Rank', 'OFF%', 'DEF%', 'OVERALL%']]
                return playerimpact
        except:
            pass

    @output
    @render.image
    def plot():
       player = chartshotlocation[chartshotlocation['Player'] == input.Player()]
       player = player.reset_index(drop=True)
       columns = player.columns[2:]
       values = player.values.flatten()[2:]
       non_zero_indices = values.nonzero()[0]
       values = values[non_zero_indices]
       columns = columns[non_zero_indices]
       fig, ax = plt.subplots(figsize=(4, 3.76))
       color = ['#005A9C', '#0072BB', '#0096D6', '#00AEEF', '#33C0E9']
       ax.pie(values, labels=columns, colors=color, autopct='%1.1f%%', labeldistance=1.1, wedgeprops = { 'linewidth' : 1, 'edgecolor' : 'white' }, textprops={'fontsize': 10})
       ax.axis('equal')
       image_path = "shot_location.png"  # Specify your desired file path and name
       plt.savefig(image_path, dpi=300, bbox_inches='tight')
       plt.close()
       from pathlib import Path
       dir = Path(__file__).resolve().parent
       img: ImgData = {"src": image_path, "width": "395px", "height": "275px"}
       return img
    
app = App(app_ui, server)
