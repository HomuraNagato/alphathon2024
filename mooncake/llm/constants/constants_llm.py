
from dataclasses import dataclass

@dataclass
class ConstantsLLM:

    advertiser: str = "advertiser"
    product_group: str = "product_group"  # campaign name
    product_name: str = "product_name"
    prompt: str = "prompt"
    prompt_destemmed: str = "prompt_destemmed"
    rules_category: str = "rules_category"
    api_model_category: str = "api_model_category"
    llm_model_category: str = "llm_model_category"
    senzai_category: str = "senzai_category"
    true_category: str = "true_category"
    client_category: str = "client_category"

    columns = [ advertiser, product_group, product_name, prompt,
                prompt_destemmed, rules_category, api_model_category,
                llm_model_category, senzai_category, true_category,
                client_category ]
    
    # map client (eng) columns to llm columns
    azteca_cols_dict = {
        "advertiser": advertiser,
        "product": product_group,
        "product_version": product_name,
        "product_real": true_category,
    }

    elektra_cols_dict = {
        "advertiser": advertiser,
        "product": product_group,
        "product_version": product_name,
        "product_real": true_category,
        "vertical": client_category
    }

    telcel_cols_dict = {
        "product": product_group,
        "product_version": product_name,
        "category": true_category
    }
