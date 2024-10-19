# Do firms’ 10-K filings tell us more information than we already know? – A perspective through fine-tuning Large Language Models (LLMs)

## Section 1 Summary

The 'Mooncake' team, comprises of three members, [Lingyi Kong](https://www.linkedin.com/in/lykong/), [Mark McAvoy](https://www.linkedin.com/in/mkmcavoy/), and [Sabrina McAvoy](https://www.linkedin.com/in/slmcavoy/), is honored to present our two-step trading strategy. First, we fine-tuned a Large Language Model (LLM) to generate 'buy' and 'sell' signals based on the analysis of 10-K filings. Second, we applied a mean-variance optimization approach to compute the portfolio weights for the stocks flagged as 'buy.' Our stock universe consists of the members of the S&P 500 index, with the in-sample period spanning from 2010 to 2018 and the out-of-sample period from 2019 to 2023, with monthly portfolio rebalancing. Our strategy outperformed the S&P 500, delivering higher cumulative returns with a comparable level of risk in both the in-sample and out-of-sample periods. Additionally, the strategy maintained a low turnover ratio, resulting in reduced transaction costs, further enhancing its overall performance.

## Section 2 Relevance

Our approach uniquely combines the power of LLMs for qualitative analysis with the rigor of mean-variance optimization for quantitative portfolio construction. While traditional stock selection methods often rely purely on financial metrics or technical indicators, our use of LLMs allows us to extract deeper insights from 10-K filings, capturing management perspectives, business risks, and operational performance that may not be immediately evident in numerical data. This integration of unstructured text analysis with a robust optimization framework enables us to not only select stocks with potential predictive signals but also allocate weights efficiently, creating a more informed and balanced portfolio.

## Section 3 Data and Portfolio Construction

Our sample spans from 2010 to 2023, with 2010 to 2018 as the in-sample period during which we developed the strategy, and 2019 to 2023 as the out-of-sample period where we tested its
performance. We analyzed firms' 10-K filings by fine-tuning ChatGPT, acquired the S&P 500 composition from CRSP, and obtained daily returns for the S&P 500 from Compustat.

Our portfolio strategy begins in January 2010, with equal weighting across all components of the S&P 500. The portfolio is rebalanced monthly based on recommendations from the LLM model.
Specifically, each time a firm releases its 10-K filing, the LLM provides a 'buy' or 'sell' signal. If the model generates a 'sell' signal, the stock is excluded from the portfolio and remains excluded until a future 10-K filing generates a 'buy' signal. For stocks receiving a 'buy' signal, their portfolio weight is determined using mean-variance optimization, along with all other stocks marked as 'buy' by the LLM. The new weighting becomes effective in the month following the firm's 10-K update. We also account for the rebalancing of the S&P 500, considering only the available stock pool consisting of the current members of the index.

The details regarding the SEC 10-K filings and LLM fine-tuning are provided below:

### Section 3.1: SEC Data Insights

Each year, U.S. public firms are required to produce a Form 10-K and file it with the U.S. SEC within 60 days of the fiscal year's end. The structure of the Form 10-K consists of four parts and 15 items. The textual data we use consists of 10-K filings from the Securities and Exchange Commission’s (SEC) EDGAR website, cleaned and provided by Professor Bill McDonald.[^1]

For the purpose of our strategy, we focus on three specific items from the Form 10-K:

  - Item 1, '*Business*', which describes the company’s business, including its main products and services, subsidiaries, and the markets in which it operates.
  - Item 1A, '*Risk Factors*', which outlines the most significant risks faced by the company.
  - Item 7, '*Management's Discussion and Analysis of Financial Condition and Results of Operations*', which presents the company’s perspective on its financial performance during the prior fiscal year.

Our interest in these three items lies in their ability to describe the nature of the business, its risks, and management’s perspective, which we believe hold potential predictive power over the firm’s future performance. Within each item, we further parse the text by splitting it into sections using the 'Table of Contents' or '\n\n' as separators. We then identify the two most important sections based on the frequency of financial keywords such as 'risk', 'performance', or 'dividend'.[^2]

### Section 3.2: LLM Fine-Tuning

We chose to use OpenAI’s GPT-4o-mini model, which we fine-tuned using the 10-K data. We combined the text from the three items into a single input for the model. To fine-tune the model,
a source of 'ground truth' is required. This serves as the target for the optimization function, guiding how the model’s weights should be adjusted to improve its performance in generating the desired results. We generated our ground truth by calculating a 30-day rolling average of the stock price for the days following the 10-K filing date. We then converted this into a boolean ‘buy’ or ‘sell’ signal, depending on whether the rolling average was greater or less than the stock price on the 10-K filing date, respectively.[^3] The process of fine tuning on OpenAI’s platform involves several steps:

  1. **Merge 10-K filings with price data** to generate the 'ground truth' (i.e., the expected output based on historical data). This involves aligning the filings' text with price movements to label whether a 'buy' or 'sell' signal should be generated.
  2. **Subset and format the data** into content tuples that specify the input (the text from the 10-K) and the expected output (in this case, 'buy' or 'sell'), and then save the formatted data in JSONL format.
  3. **Upload the JSONL file to OpenAI** and wait for a model ID to be returned, indicating that the fine-tuning process is complete. The platform will process the data and train the LLM to understand how textual elements in the 10-K filings relate to price movements.
  4. **Save the model ID** for use in evaluating and testing the fine-tuned model and use it to evaluate the model’s performance on unseen data. This involves feeding new 10-K filings through the model to see how accurately it predicts 'buy' or 'sell' signals based on the text.

LLMs are primarily designed to process and generate text, so we avoid confounding the model by asking it to provide specific portfolio weights. Instead, we use the LLM to narrow down our selection of stocks, and then determine the portfolio weights using mean-variance optimization.[^4] In this way, we leverage the LLM for qualitative analysis while relying on mean-variance optimization for quantitative portfolio construction.

[^1]: The cleaned 10-K filings can be found at: [https://sraf.nd.edu/sec-edgar-data/cleaned-10x-files/](https://sraf.nd.edu/sec-edgar-data/cleaned-10x-files/), and the parsing procedure is available at: [https://sraf.nd.edu/sec-edgar-data/cleaned-10x-files/10x-stage-one-parsing-documentation/](https://sraf.nd.edu/sec-edgar-data/cleaned-10x-files/10x-stage-one-parsing-documentation/).

[^2]: A short demonstration of this can be seen at the following Jupyter notebook: [https://github.com/HomuraNagato/alphathon2024/blob/main/mooncake/text_from_10ks.ipynb](https://github.com/HomuraNagato/alphathon2024/blob/main/mooncake/text_from_10ks.ipynb).

[^3]: There are numerous ways to generate ground truth, and we selected a method that is relatively straightforward and intuitive given time constraints. However, exploring alternative approaches could potentially improve the results and provide further insights.

[^4]: We acknowledge that there are other ways to optimize the portfolio given the stock pool; however, for the sake of time, we chose the method that offers the most intuitive way to balance mean and variance and achieve a portfolio on the efficient frontier.

## Section 4 Results

### Section 4.1: In-sample Results

Our in-sample results demonstrate that we were able to outperform the S&P 500, as illustrated in Figure 1, which compares the cumulative returns of the S&P 500 with those of our strategy over the sample period from 2010 to 2018.

A closer look of our strategy performance is provided in QuantConnect report:[^5] Our strategy significantly outperformed the S&P 500 in terms of annual returns, with a CAGR of 15.7% compared to the S&P 500's historical average of around 10-12% over the same period. Despite this higher return, the strategy maintained a solid risk profile, reflected in a Sharpe ratio of 0.8, which is comparable to the S&P 500’s long-term Sharpe ratio of approximately 0.9. This indicates that while our strategy took on a similar level of risk, it achieved greater returns. The maximum drawdown of 17.1% shows effective downside risk management, which is in line with or better than the S&P 500 during periods of market volatility.

Furthermore, the strategy maintained a low turnover rate of 1%, resulting in fewer trades and lower transaction costs, with an average of 0.4 trades per day, reflecting its conservative
approach. The information ratio of 0.9 highlights the strategy's ability to generate excess returns relative to the S&P 500, demonstrating its effectiveness in capturing alpha. Overall, our approach not only delivered higher returns but also managed risk and transaction costs efficiently, making it a strong alternative to the passive S&P 500 strategy.

The performance of our strategy is closely tied to its design. Since Form 10-K is released only once per year, with most filings occurring in the spring, our portfolio rebalances infrequently, as updates for each firm are available only annually. Despite this, we were able to outperform the S&P 500 using only this information. This infrequent rebalancing leads to a lower turnover ratio and fewer trades, minimizing transaction costs. We believe our strategy could be further strengthened by incorporating other financial statement data that is released more frequently, such as the firm's 10-Q filings and earnings call transcripts, allowing for more frequent updates and potentially even better performance.

[^5]: [https://www.quantconnect.com/reports/17c7e8fd4abaecad5a30ef3aca86a69f](https://www.quantconnect.com/reports/17c7e8fd4abaecad5a30ef3aca86a69f)

### Section 4.2: Out-of-Sample Results

Our out-of-sample results from 2019 to 2023 show that while our strategy maintained solid performance, it faced more challenging conditions compared to the in-sample period.[^6] The strategy achieved a CAGR of 11.4%, closely matching the S&P 500’s CAGR of approximately 11% during the same period. However, the maximum drawdown of 27.9% reflects higher volatility than the S&P 500's drawdowns over these years. The strategy's Sharpe ratio of 0.5 was slightly below the S&P 500’s Sharpe ratio of 0.6, indicating that while our strategy delivered competitive returns, it took on marginally higher risk.

Despite the increased volatility, the strategy maintained a turnover rate of 2% and averaged 0.6 trades per day, which still represents a relatively conservative approach. The information ratio of 0.6 demonstrates that the strategy continued to generate excess returns relative to the benchmark, though at a lower level compared to the in-sample period. Overall, our strategy managed to keep pace with the S&P 500 in terms of returns, but with slightly more risk during this more turbulent period, reinforcing the robustness of the approach across varying market conditions.

A potential explanation for the lower performance during the out-of-sample period from 2019 to 2023 could be the stark difference in market conditions compared to the in-sample period (2010 to 2018). The in-sample period largely captures the post-2008 financial crisis recovery, which was marked by a long bull market with relatively low volatility and strong growth. In contrast, the out-of-sample period includes the COVID-19 pandemic in 2020, which caused significant market disruptions, sharp declines, and subsequent rapid recoveries. The pandemic brought about heightened volatility and uncertainty, conditions that were likely not fully accounted for by the model trained on a more stable and bullish market.[^7]

[^6]: [https://www.quantconnect.com/reports/2fcf96cc0420e820ed2d17c5200d4c87](https://www.quantconnect.com/reports/2fcf96cc0420e820ed2d17c5200d4c87)

[^7]: There are several ways we can train our model to account for economic cycles and major events. One approach is to use cross-validation, partitioning the sample in different ways to ensure the model is exposed to diverse market conditions, including both bull and bear markets. Another potential remediation is to incorporate time-series modeling techniques that explicitly account for macroeconomic variables, such as interest rates, inflation, and unemployment, which could influence stock performance during volatile periods. Additionally, expanding the training data to include major economic downturns like the 2008 financial crisis could improve the model’s ability to handle future crises. Stress testing the model under various market conditions and incorporating rolling-window backtesting could also enhance its robustness, helping it adapt better to different market environments and reducing the impact of unexpected shocks like the COVID-19 pandemic.

## Section 5 Conclusions

In this project, we constructed a monthly-rebalanced portfolio by leveraging Form 10-K information extracted using an LLM to select the stocks for investment, and a mean-variance trade-off strategy to determine their weights. Despite the simplicity of the strategy, it outperforms the S&P 500 in terms of cumulative returns while maintaining a comparable level of risk and low transaction costs. So, to answer the question posed at the very beginning—Do firms' 10-K filings tell us more than we already know? The answer is clearly yes, as we were able to generate outperformance using a strategy based on a simple extraction from 10-K filings.

Admittedly, there are several areas for improvement that we were unable to address due to time constraints. First, the universe of corporate textual documents is vast, with many being released more frequently, such as 10-Q filings and earnings call transcripts, which are issued quarterly. Additionally, social media platforms such as WallStreetBets on Reddit and StockTwits provide valuable insights from both professional and retail investors, which could be incorporated into the fine-tuning of the LLM. Ideally, by combining official company documents with investor opinions, we could achieve a more frequently balanced portfolio with an improved return-risk tradeoff. The second improvement we would like to incorporate is an investigation of the alpha generated by our strategy, rather than just focusing on raw returns. It would be beneficial to regress our portfolio returns against a set of known factors, such as the Fama-French three factors and momentum factors, to determine whether we are outperforming the S&P 500 in terms of both excess and abnormal returns.

Despite these potential improvements, our simple strategy outperforms the S&P 500 with a low turnover ratio, highlighting the potential of our approach as we continue to refine and expand the information our LLM is fine-tuned on, as well as increase the frequency of portfolio rebalancing. This project highlights the important role textual information plays in understanding a firm’s operations and predicting its future price movements, which are often more challenging to process compared to numerical data like profit and loss. Our team has no doubt that LLMs will become one of the most powerful tools for extracting hidden information embedded in corporate documents and reshaping the way the industry invests.

## Appendix

## Supporting Links to the Report

In-Sample Results

  - Results from QuantConnect: [https://www.quantconnect.com/reports/17c7e8fd4abaecad5a30ef3aca86a69f](https://www.quantconnect.com/reports/17c7e8fd4abaecad5a30ef3aca86a69f)
  - Code:
    - GitHub: [https://github.com/HomuraNagato/alphathon2024/tree/main/mooncake](https://github.com/HomuraNagato/alphathon2024/tree/main/mooncake)
    - QuantConnect: [https://www.quantconnect.com/terminal/clone/-/17c7e8fd4abaecad5a30ef3aca86a69f/clone-of%3A-focused-violet-baboon]( https://www.quantconnect.com/terminal/clone/-/17c7e8fd4abaecad5a30ef3aca86a69f/clone-of%3A-focused-violet-baboon) - This link may require an invitation from our team members, as it is part of the project domain we created within QuantConnect. If the judges are unable to access it through QuantConnect’s backend system, we are happy to share our workspace as long as we receive the emails of those who need to be invited.
  -  Spreadsheets:
    - [https://www.quantconnect.com/terminal/processCache?request=embedded_backtest_17c7e8fd4abaecad5a30ef3aca86a69f.html](https://www.quantconnect.com/terminal/processCache?request=embedded_backtest_17c7e8fd4abaecad5a30ef3aca86a69f.html)

Out-of-Sample Results

  - Results from QuantConnect:
    - [https://www.quantconnect.com/reports/2fcf96cc0420e820ed2d17c5200d4c87](https://www.quantconnect.com/reports/2fcf96cc0420e820ed2d17c5200d4c87)
  - Code:
    - GitHub: [https://github.com/HomuraNagato/alphathon2024/tree/main/mooncake](https://github.com/HomuraNagato/alphathon2024/tree/main/mooncake)
    - QuantConnect: [https://www.quantconnect.com/terminal/clone/-/17c7e8fd4abaecad5a30ef3aca86a69f/clone-of%3A-focused-violet-baboon]( https://www.quantconnect.com/terminal/clone/-/17c7e8fd4abaecad5a30ef3aca86a69f/clone-of%3A-focused-violet-baboon) - This link may require an invitation from our team members, as it is part of the project domain we created within QuantConnect. If the judges are unable to access it through QuantConnect’s backend system, we are happy to share our workspace as long as we receive the emails of those who need to be invited.
  -  Spreadsheets:
    - [https://www.quantconnect.com/terminal/processCache?request=embedded_backtest_2fcf96cc0420e820ed2d17c5200d4c87.html](https://www.quantconnect.com/terminal/processCache?request=embedded_backtest_2fcf96cc0420e820ed2d17c5200d4c87.html)

      
