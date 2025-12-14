import requests
from langchain.tools import tool


@tool
def generate_chart(
    data: str,
    chart_type: str = "bar",
    title: str = "Chart",
    output_file: str = "chart.png",
) -> str:
    """Generate charts from data.

    Args:
        data: CSV data or JSON data
               Example CSV: "name,value\nA,10\nB,20\nC,15"
               Example JSON: '[{"name": "A", "value": 10}]'
        chart_type: 'bar', 'pie', 'line', 'histogram', 'scatter', 'box'
        title: Chart title
        output_file: Where to save chart

    Returns:
        Path to saved chart
    """
    try:
        import json

        import matplotlib.pyplot as plt
        import pandas as pd

        # Parse data
        if data.strip().startswith("["):
            # JSON format
            data_list = json.loads(data)
            df = pd.DataFrame(data_list)
        else:
            # CSV format
            from io import StringIO

            df = pd.read_csv(StringIO(data))

        if df.empty:
            return "❌ Data is empty"

        # Create chart based on type
        plt.figure(figsize=(10, 6))

        if chart_type == "bar":
            # Bar chart
            df.set_index(df.columns[0]).plot(kind="bar")
            plt.title(title)
            plt.ylabel("Values")
            plt.xlabel("Categories")

        elif chart_type == "pie":
            # Pie chart
            plt.pie(df[df.columns[1]], labels=df[df.columns[0]], autopct="%1.1f%%")
            plt.title(title)

        elif chart_type == "line":
            # Line chart
            for col in df.columns[1:]:
                plt.plot(df[df.columns[0]], df[col], marker="o", label=col)
            plt.title(title)
            plt.xlabel(df.columns[0])
            plt.ylabel("Values")
            plt.legend()

        elif chart_type == "histogram":
            # Histogram
            plt.hist(df[df.columns[0]], bins=20, edgecolor="black")
            plt.title(title)
            plt.xlabel("Values")
            plt.ylabel("Frequency")

        elif chart_type == "scatter":
            # Scatter plot
            plt.scatter(df[df.columns[0]], df[df.columns[1]])
            plt.title(title)
            plt.xlabel(df.columns[0])
            plt.ylabel(df.columns[1])

        elif chart_type == "box":
            # Box plot
            df.plot(kind="box")
            plt.title(title)

        else:
            return f"❌ Chart type '{chart_type}' not supported"

        # Save
        plt.tight_layout()
        plt.savefig(output_file, dpi=100, bbox_inches="tight")
        plt.close()

        return f"✅ Chart saved: {output_file}"

    except json.JSONDecodeError:
        return "❌ Invalid JSON format"

    except pd.errors.ParserError:
        return "❌ Invalid CSV format"

    except Exception as e:
        return f"❌ Chart generation failed: {str(e)}"
