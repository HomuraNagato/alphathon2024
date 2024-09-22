15Sep2014 - without CIK indicator: https://www.dropbox.com/scl/fi/gv4s5v9lnydoz7o4141kl/sp500list.sas7bdat?rlkey=ztir4oo3ppayimz3kyhhmy0v7&dl=0

**updated** 15Sep2014 -- with CIK indicator: https://www.dropbox.com/scl/fi/vn01g2uboew3nemgelxie/sp500cik.sas7bdat?rlkey=nxi030m7rzk72x57hoz7tfqv2&dl=0

**updated** 22Sep2024 -- with *adjusted* price & *adjusted* shares outstanding & market capitalization: https://www.dropbox.com/scl/fi/hpnf7gk1p77m9icyoqiei/sp500cik.sas7bdat?rlkey=5ngtjlfaj1ui83byl0a4jyhcy&dl=0

            variable description:
            
            - DATE: Date of Observation, in format of YYYYMMDD
            
            - TICKER: Exchange Ticker Symbol
            
            - PERMNO: unique stock identifier created by Center for Research in Security Prices, LLC (CRSP)
            
            - SHRCD: Share Code (e.g, whether it is a common stock or else)
            
            - EXCHCD: Exchange Code (1 = NYSE, 3 = NASDAQ, 2 = AMEX)
            
            - PRC: Price or Bid/Ask Average
            
            - RET: Returns
            
            - SHROUT: Shares Outstanding
            
            - CFACPR: Cumulative Factor to Adjust Prices (e.g., in case of stock split)
            
            - CFACSHR: Cumulative Factor to Adjust Shares/Vol (e.g., in case of stock split)
            
            - start: Date when the stock included in S&P500 Index
            
            - ending: Date when the stock excluded from SP500 Index
            
            - gvkey: Standard and Poor's Identifier
            
            - cik: CIK Number (to link with SEC documents)
            
            - sic: Standard Industry Classification Code
            
            - naics: North American Industry Classification Code
            
            - gind: GIC Industries
            
            - gsubind: GIC Sub-Industries

**newly added variables on 22Sep**

            - BIDLO: lowest trading price during the day, or the closing bid price on days when the closing price is not available.

            - ASKHI: highest trading price during the day, or the closing ask price on days when the closing price is not available.

            - OPENPRC: the first trading price after market opens

            - PRC_Adj (= PRC / CFACPR): adjusted prices for corporate events such as share splits 

            - SHROUT_Adj (= SHROUT * CFACSHR): adjusted shares outstanding for corporate events such as share splits 

            - mktcap (= abs(prc)*shrout): market capitalization 
