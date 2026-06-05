import pandas as pd
import streamlit as st

def render_results(result: dict, engine: str):
    """
    Renders the OCR and translation results.

    Args:
        result (dict): The result dictionary from the backend.
        engine (str): The selected OCR engine identifier.
    """
    st.subheader("Results")

    if engine == "compare":
        results_list = result.get("results", [])
        if results_list:
            cols = st.columns(len(results_list))
            for i, r in enumerate(results_list):
                with cols[i]:
                    st.markdown(f"**{r['engine']}**")
                    st.caption(f"{r['execution_time_ms']} ms")
                    st.markdown("Extracted Text:")
                    st.code(r["extracted_text"], language=None)
                    st.markdown("Translated Text:")
                    st.code(r["translated_text"], language=None)

                    # Japanese Analysis expander per engine
                    analysis = r.get("advanced_analysis")
                    if analysis:
                        df = pd.DataFrame(analysis)
                        df.index = df.index + 1
                        st.dataframe(df, use_container_width=True)

            st.markdown("**Performance Comparison**")
            chart_data = pd.DataFrame({
                "Engine": [r["engine"] for r in results_list],
                "Latency (ms)": [r["execution_time_ms"] for r in results_list],
            })
            st.bar_chart(chart_data, x="Engine", y="Latency (ms)")
    else:
        st.caption(f"Engine: **{result.get('engine')}** | {result.get('execution_time_ms')} ms")

        text_col, translation_col = st.columns([1, 1])

        with text_col:
            st.markdown("**Extracted Text**")
            st.code(result.get("extracted_text", ""), language=None)

        with translation_col:
            st.markdown("**Translated Text**")
            st.code(result.get("translated_text", ""), language=None)

        # Japanese Analysis expander for single mode
        analysis = result.get("advanced_analysis")
        if analysis:
            df = pd.DataFrame(analysis)
            df.index = df.index + 1
            st.dataframe(df, use_container_width=True)
