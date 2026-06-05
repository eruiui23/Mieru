"""OCR results display components."""

import pandas as pd
import requests
import streamlit as st

import api_client


def render_results(settings: dict) -> None:
    """Render the process button and results display."""
    # Get the current image index from session state
    idx = st.session_state.get("image_selector", 0)
    engine = settings["engine"]
    target_lang = settings["target_lang"]

    st.divider()

    if st.button("Process Image", type="primary", key=f"process_{idx}"):
        image_bytes = st.session_state.get(f"processed_image_bytes_{idx}")

        if image_bytes is None:
            st.error("No processed image available.")
        else:
            with st.spinner("Processing OCR..."):
                try:
                    if engine == "compare":
                        result = api_client.process_compare(image_bytes, target_lang)
                    else:
                        result = api_client.process_single(image_bytes, engine, target_lang)

                    st.session_state[f"ocr_result_{idx}"] = result

                except requests.ConnectionError:
                    st.error(
                        "Could not connect to the backend server. "
                        "Make sure it's running on http://localhost:8000"
                    )
                except requests.HTTPError as e:
                    st.error(f"Backend error: {e.response.json().get('detail', str(e))}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    # Display results
    st.subheader("Results")

    if f"ocr_result_{idx}" not in st.session_state:
        return

    result = st.session_state[f"ocr_result_{idx}"]

    if engine == "compare":
        _render_comparison_results(result)
    else:
        _render_single_results(result)


def _render_comparison_results(result: dict) -> None:
    """Render side-by-side comparison results with performance chart."""
    results_list = result.get("results", [])
    if not results_list:
        return

    cols = st.columns(len(results_list))
    for i, r in enumerate(results_list):
        with cols[i]:
            st.markdown(f"**{r['engine']}**")
            st.caption(f"{r['execution_time_ms']} ms")
            st.markdown("Extracted Text:")
            st.code(r["extracted_text"], language=None)
            st.markdown("Translated Text:")
            st.code(r["translated_text"], language=None)

            # Japanese Analysis
            _render_analysis(r.get("advanced_analysis"))

    st.markdown("**Performance Comparison**")
    chart_data = pd.DataFrame({
        "Engine": [r["engine"] for r in results_list],
        "Latency (ms)": [r["execution_time_ms"] for r in results_list],
    })
    st.bar_chart(chart_data, x="Engine", y="Latency (ms)")


def _render_single_results(result: dict) -> None:
    """Render single-engine OCR results."""
    st.caption(f"Engine: **{result.get('engine')}** | {result.get('execution_time_ms')} ms")

    text_col, translation_col = st.columns([1, 1])

    with text_col:
        st.markdown("**Extracted Text**")
        st.code(result.get("extracted_text", ""), language=None)

    with translation_col:
        st.markdown("**Translated Text**")
        st.code(result.get("translated_text", ""), language=None)

    # Japanese Analysis
    _render_analysis(result.get("advanced_analysis"))


def _render_analysis(analysis: list | None) -> None:
    """Render the Japanese text analysis expander if data is available."""
    if not analysis:
        return

    with st.expander("文法 & 振り仮名 | Japanese Analysis (Furigana & Readings)"):
        df = pd.DataFrame(analysis)
        df.index = df.index + 1
        st.dataframe(df, use_container_width=True)
