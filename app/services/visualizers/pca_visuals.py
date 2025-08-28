import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns


class DegAnalysisPCAVisualizer:
    """
    Visualizer: plotting only. Consumes outputs produced by DegAnalysisPCA.
    """

    def __init__(
        self,
        pc_df: pd.DataFrame,
        loadings_df: pd.DataFrame,
        meta_df_grpcol: str = "subgroup",
        n_components: int = 3,
    ):
        self._pc_df = pc_df
        self._loadings_df = loadings_df
        self.meta_df_grpcol = meta_df_grpcol
        self.n_components = n_components

    # -------- PCA visuals --------
    def plot_pca_3D(
        self,
        title: str = "PCA 3D Plot",
        sample_id_column: str = "sample_id",
        notebook: bool = True,
    ):
        if self.n_components < 3:
            raise ValueError("plot_pca_3D requires n_components >= 3.")

        fig = px.scatter_3d(
            self._pc_df,
            x="PC1",
            y="PC2",
            z="PC3",
            color=self.meta_df_grpcol,
            hover_data=[sample_id_column, self.meta_df_grpcol],
            title=title,
        )

        return fig

    def plot_pca_loadings_grid(self, pcs: list[str] | None = None, top_n: int = 10):
        if pcs is None:
            pcs = [f"PC{i+1}" for i in range(self.n_components)]

        n_pcs = len(pcs)
        n_cols = min(3, n_pcs)
        n_rows = int(np.ceil(n_pcs / n_cols))

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 5 * n_rows), squeeze=False)

        for idx, pc in enumerate(pcs):
            row = idx // n_cols
            col = idx % n_cols
            ax = axes[row, col]

            pc_series = self._loadings_df.set_index("gene")[pc]
            top_pos = pc_series.sort_values(ascending=False).head(top_n)
            top_neg = pc_series.sort_values().head(top_n)
            top_combined = pd.concat([top_neg, top_pos])

            ax.barh(y=top_combined.index, width=top_combined.values)
            ax.axvline(0, linewidth=0.8)
            ax.grid(axis="x", linestyle="--", alpha=0.5)
            ax.set_title(f"{pc}: Top ±{top_n} Loadings", fontsize=12)
            ax.set_xlabel("Loading", fontsize=11)
            ax.set_ylabel("Gene", fontsize=11)

        # Remove any empty axes
        total_subplots = n_rows * n_cols
        for i in range(n_pcs, total_subplots):
            fig.delaxes(axes.flatten()[i])

        plt.tight_layout()
        plt.show()

    # -------- Heatmaps (matplotlib-based) --------
    def plot_subgroup_avg_heatmap(self, avg_expr: pd.DataFrame, title: str = "Average Gene Expression per Subgroup"):
        plt.figure(figsize=(8, 6))
        im = plt.imshow(avg_expr, aspect="auto")
        plt.colorbar(im, label="Average Expression Level")
        plt.title(title)
        plt.xlabel("Subgroup")
        plt.ylabel("Gene")
        plt.xticks(ticks=np.arange(len(avg_expr.columns)), labels=avg_expr.columns, rotation=0, ha="right")
        plt.yticks(ticks=np.arange(len(avg_expr.index)), labels=avg_expr.index)
        plt.tight_layout()
        plt.show()

    def plot_subgroup_avg_heatmaps_per_pc(self, pc_avg_exprs: dict[str, pd.DataFrame], notebook: bool = True):
        """
        pc_avg_exprs = { 'PC1': DataFrame, 'PC2': DataFrame, ... }
        Produces interactive Plotly heatmaps per PC.
        """
        figs = []
        for pc, avg_expr in pc_avg_exprs.items():
            fig = px.imshow(
                avg_expr,
                labels=dict(x="Subgroup", y="Gene", color="Avg Expression"),
                x=avg_expr.columns,
                y=avg_expr.index,
                title=f"{pc}: Avg Expression by Subgroup",
            )
            figs.append(fig)

        return figs


class DegAnalysisLimmaVoomVisualizer:
    """
    Visualize the output of DegAnalysisLimmaVoomProcessor.
    Supports notebook display via display_html or Dash via figure return.
    """

    def __init__(self, deg_result_df: pd.DataFrame):
        self.deg_result_df = deg_result_df

    def volcano_plot(self, logfc_col: str = "log_fc", pval_col: str = "adj_p_value", notebook: bool = True):
        pdf = self.deg_result_df.copy()

        # Ensure numeric types
        pdf[logfc_col] = pd.to_numeric(pdf[logfc_col], errors="coerce")
        pdf[pval_col] = pd.to_numeric(pdf[pval_col], errors="coerce")

        # Drop rows with NaN values in those cols
        pdf = pdf.dropna(subset=[logfc_col, pval_col])

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(pdf[logfc_col], -np.log10(pdf[pval_col]), alpha=0.6)
        ax.set_xlabel("log2 Fold Change")
        ax.set_ylabel("-log10 FDR")
        ax.set_title("Limma-Voom Volcano Plot")
        ax.axhline(-np.log10(0.05), color="red", linestyle="--")
        ax.axvline(0, color="grey", linestyle="--")
        plt.tight_layout()

        if notebook:
            plt.show()
        else:
            return fig


    def top_genes_table(self, n: int = 20) -> pd.DataFrame:
        pdf = self.deg_result_df.sort_values(by="adj_p_value", ascending=True)
        return pdf.head(n)

    def plot_top_logfc(self, n: int = 20, logfc_col: str = "log_fc", title: str = "Top LogFC Genes", notebook: bool = True) -> plt.Figure | None:
        """
        Plot the top n genes by absolute log fold change.
        """
        df = self.deg_result_df 
        df['abs_logFC'] = df[logfc_col].abs()
        top_df = df.nlargest(n, 'abs_logFC')
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=logfc_col, y="gene", data=top_df, palette="viridis", ax=ax)
        ax.set_title(title)
        ax.set_xlabel("Log Fold Change")
        ax.set_ylabel("gene")
        plt.tight_layout()

        return fig
