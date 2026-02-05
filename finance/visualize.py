# visualize.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib as mpl

# macOS 한글 폰트 설정
mpl.rcParams["font.family"] = "AppleGothic"
mpl.rcParams["axes.unicode_minus"] = False  # 마이너스 깨짐 방지

def plot_equity_curve(
    result: pd.DataFrame,
    title: str = "Equity Curve"
):
    """
    포트폴리오 누적 자산 그래프
    """

    df = result.sort_values("Date")

    plt.figure(figsize=(10, 5))
    plt.plot(df["Date"], df["Total Balance"])
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Total Balance")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_drawdown(
    result: pd.DataFrame,
    title: str = "Drawdown"
):
    """
    Drawdown 그래프
    """

    df = result.sort_values("Date")

    balance = df["Total Balance"]
    drawdown = balance / balance.cummax() - 1

    plt.figure(figsize=(10, 4))
    plt.plot(df["Date"], drawdown)
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.grid(True)
    plt.tight_layout()
    plt.show()



def plot_returns_bar(result, title="Annual Returns"):
    df = (
        result[["Date", "Total Return"]]
        .dropna()
        .sort_values("Date")
        .reset_index(drop=True)
    )

    plt.figure(figsize=(10, 4))

    # width = 200 days (연간 데이터에 적당)
    plt.bar(
        df["Date"],
        df["Total Return"],
        width=200
    )

    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Return")
    plt.grid(True)
    plt.tight_layout()
    plt.show()



def plot_equity_curves(
    results,
    title: str = "Equity Curve"
):
    """
    여러 포트폴리오 누적 자산 비교 그래프

    results:
        - pd.DataFrame
        - dict[str, pd.DataFrame]
    """

    plt.figure(figsize=(10, 5))

    if isinstance(results, dict):
        for name, df in results.items():
            d = df.sort_values("Date")
            plt.plot(d["Date"], d["Total Balance"], label=name)

        plt.legend()

    else:
        d = results.sort_values("Date")
        plt.plot(d["Date"], d["Total Balance"])

    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Total Balance")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_drawdowns(
    results,
    title: str = "Drawdown"
):
    """
    여러 포트폴리오 Drawdown 비교
    """

    plt.figure(figsize=(10, 4))

    if isinstance(results, dict):
        for name, df in results.items():
            d = df.sort_values("Date")
            balance = d["Total Balance"]
            drawdown = balance / balance.cummax() - 1
            plt.plot(d["Date"], drawdown, label=name)

        plt.legend()

    else:
        d = results.sort_values("Date")
        balance = d["Total Balance"]
        drawdown = balance / balance.cummax() - 1
        plt.plot(d["Date"], drawdown)

    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_returns_bars(
    results,
    title="Periodic Returns"
):
    """
    여러 전략 수익률 비교 (subplot)
    """

    if isinstance(results, dict):
        n = len(results)
        fig, axes = plt.subplots(n, 1, figsize=(10, 3 * n), sharex=True)

        if n == 1:
            axes = [axes]

        for ax, (name, df) in zip(axes, results.items()):
            d = (
                df[["Date", "Total Return"]]
                .dropna()
                .sort_values("Date")
            )

            ax.bar(d["Date"], d["Total Return"], width=200)
            ax.set_title(name)
            ax.grid(True)

        fig.suptitle(title)
        plt.tight_layout()
        plt.show()

    else:
        df = (
            results[["Date", "Total Return"]]
            .dropna()
            .sort_values("Date")
        )

        plt.figure(figsize=(10, 4))
        plt.bar(df["Date"], df["Total Return"], width=200)
        plt.title(title)
        plt.grid(True)
        plt.tight_layout()
        plt.show()