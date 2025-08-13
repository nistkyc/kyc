import re
from typing import Dict, Optional, List
import streamlit as st

class DataParser:
    """Parses extracted text to identify and extract specific data fields"""
    
    def __init__(self):
        # Define patterns for clean data extraction
        self.patterns = {
            'name': [
                r'Name[:\s]+([A-Z][A-Z\s]+?)(?=\s*(?:Date of Birth|Gender|Father|Mother|Occupation|$|\n))',
                r'gfd[:\s]+([A-Z][A-Z\s]+?)(?=\s*(?:hGd ldlt|ln·|$|\n))',
                r'Name \(In Block Letter\)[:\s]+([A-Z][A-Z\s]+?)(?=\s*(?:Date of Birth|Gender|$|\n))'
            ],
            'date_of_birth': [
                r'Date of Birth[:\s]+AD[:\s]*(\d{4}-\d{2}-\d{2})',
                r'AD[:\s]*:\s*(\d{4}-\d{2}-\d{2})',
                r'hGd ldlt[:\s]+O\{=[:\s]*(\d{4}-\d{2}-\d{2})'
            ],
            'gender': [
                r'Gender[:\s]+([MF])(?=\s*(?:Nationality|Citizenship|$|\n))',
                r'ln·[:\s]+([MF])(?=\s*(?:/fli6«otf|gful/stf|$|\n))'
            ],
            'citizenship_no': [
                r'Citizenship No[.:]?\s*(\d+)(?=\s*(?:Issue|District|hf/L|lhNnf))',
                r'Citizenship Number[:\s]*(\d+)(?=\s*(?:Issue|District|hf/L|lhNnf))',
                r'gful/stf gDa/[:\s]*(\d+)(?=\s*(?:Issue|District|hf/L|lhNnf))',
                r'gful/stf g+=[:\s]*(\d+)(?=\s*(?:Issue|District|hf/L|lhNnf))',
                r'Citizenship[:\s]*(\d+)(?=\s*(?:Issue|District|hf/L|lhNnf))',
                r'(?<!Date\s)(?<!Birth\s)(\d{3,6})(?=\s*(?:Issue|District|hf/L|lhNnf))',


            ],
            'beneficiary_id': [
                r'Beneficiary ID No[.:]?\s*(\d+)',
                r'Beneficiary ID Number[:\s]*(\d+)',
                r'Beneficiary.*?ID.*?(\d+)',
                r'ID.*?No[.:]?\s*(\d+)',
                r'lxtu|fxL.*?vftf g+=[:\s]*(\d+)',
                r'lxtu|fxL.*?(\d+)',
                r'Beneficiary.*?(\d+)'
            ],
            'pan_no': [
                r'Permanent Account No[.:]?\s*\(PAN\)[:\s]*([A-Z0-9]{9,12})',
                r'PAN[:\s]*([A-Z0-9]{9,12})(?!\s*(?:ies|No|Number))',
                r':yfoL n]vf g+=[:\s]*([A-Z0-9]{9,12})'
            ],
             'issue_district': [
                r'Citizenship\s+Details[\s\S]{0,100}?Issue\s+District[:\s]*([A-Za-z\s]+?)(?=\s*(?:Issue\s+Date|Beneficiary|$|\n))',
                r'Issue\s+District[:\s]*([A-Za-z\s]+?)(?=\s*(?:Issue\s+Date|Beneficiary|$|\n))'
            ],
            'issue_date': [
                r'Issue Date\s+(\d{4}-\d{2}-\d{2})',
                r'hf/L ldlt[:\s]*(\d{4}-\d{2}-\d{2})'
            ],
            'national_id': [
                r'National ID No[.:]?\s*(\d+)',
                r'National ID Number[:\s]*(\d+)',
                r'/fli6«o kl/ro kq g+=[:\s]*(\d+)'
            ],
            'current_address': {
                'country': [
                    r'Current\s+Address[:\s]*.*?Country[:\s]*([A-Za-z\s]+?)(?=\s*(?:Province|District|$|\n))',
                    r'(?:^|\n)(?!.*Permanent)(?!.*Temporary).*?Country[:\s]+([A-Za-z\s]+?)(?=\s*(?:Province|District|$|\n))',
                ],
                'province': [
                    r'Current\s+Address[:\s]*.*?Province[:\s]*([A-Za-z0-9_\s]+?)(?=\s*(?:District|Municipality|$|\n))',
                    r'(?:^|\n)(?!.*Permanent)(?!.*Temporary).*?Province[:\s]+([A-Za-z0-9_\s]+?)(?=\s*(?:District|Municipality|$|\n))',
                ],
                 'district': [
                    r'Current\s+Address[\s\S]{0,100}?District[:\s]*([A-Za-z\s]+?)(?=\s*(?:Municipality|Ward|Tole|$|\n))',
                    r'\bCurrent\s+District[:\s]*([A-Za-z\s]+?)(?=\s*(?:Municipality|Ward|Tole|$|\n))'
                ],
                'municipality': [
                    r'Current\s+Address[:\s]*.*?Municipality[:\s]*([A-Za-z\s]+?)(?=\s*(?:Ward|Tole|$|\n))',
                    r'(?:^|\n)(?!.*Permanent)(?!.*Temporary).*?Municipality[:\s]+([A-Za-z\s]+?)(?=\s*(?:Ward|Tole|$|\n))',
                ],
                'ward_no': [
                    r'Current\s+Address[:\s]*.*?Ward No[.:]?\s*(\d+)(?=\s*(?:Tole|Telephone|Mobile|Email|$|\n))',
                    r'(?:^|\n)(?!.*Permanent)(?!.*Temporary).*?Ward No[.:]?\s*(\d+)(?=\s*(?:Tole|Telephone|Mobile|Email|$|\n))',
                ],
                'tole': [
                    r'Current\s+Address[:\s]*.*?Tole[:\s]*([A-Za-z\s]+?)(?=\s*(?:Telephone|Mobile|Email|$|\n))',
                    r'(?:^|\n)(?!.*Permanent)(?!.*Temporary).*?Tole[:\s]+([A-Za-z\s]+?)(?=\s*(?:Telephone|Mobile|Email|$|\n))',
                ],
                'telephone': [
                    r'Current\s+Address[:\s]*.*?Telephone No[.:]?\s*(\d+)(?=\s*(?:Mobile|Email|Permanent|$|\n))',
                    r'(?:^|\n)(?!.*Permanent)(?!.*Temporary).*?Telephone No[.:]?\s*(\d+)(?=\s*(?:Mobile|Email|$|\n))',
                ],
                'mobile': [
                    r'Current\s+Address[:\s]*.*?Mobile No[.:]?\s*(\d+)(?=\s*(?:Email|Permanent|Temporary|$|\n))',
                    r'(?:^|\n)(?!.*Permanent)(?!.*Temporary).*?Mobile No[.:]?\s*(\d+)(?=\s*(?:Email|$|\n))',
                ],
                'email': [
                    r'Current\s+Address[:\s]*.*?Email ID[:\s]*([A-Za-z0-9@._\-]+?)(?=\s*(?:Mobile|Permanent|Temporary|$|\n))',
                    r'(?:^|\n)(?!.*Permanent)(?!.*Temporary).*?Email ID[:\s]+([A-Za-z0-9@._\-]+?)(?=\s*(?:$|\n))',
                ]
            },
            'permanent_address': {
                'country': [
                    r'Permanent Address[:\s]*.*?Country[:\s]*([A-Za-z\s]+?)(?=\s*(?:Province|District|$|\n))',
                    r'Permanent.*?Country[:\s]*([A-Za-z\s]+?)(?=\s*(?:Province|District|$|\n))',
                    r':yfoL 7]ufgf[:\s]*.*?b]z[:\s]*([A-Za-z\s]+?)(?=\s*(?:k|b]z|lhNnf|$|\n))',
                    r'Permanent.*?Country[:\s]*([A-Za-z\s]+)',
                    r'Country[:\s]*([A-Za-z\s]+?)(?=.*?Province)',
                    r'(?:Country|b]z)[:\s]*([A-Za-z\s]+?)(?=\s*(?:Province|k|b]z|District|lhNnf))'
                ],
                'province': [
                    r'Permanent Address[:\s]*.*?Province[:\s]*([A-Za-z0-9_\s]+?)(?=\s*(?:District|Municipality|$|\n))',
                    r'Permanent.*?Province[:\s]*([A-Za-z0-9_\s]+?)(?=\s*(?:District|Municipality|$|\n))',
                    r':yfoL 7]ufgf[:\s]*.*?k|b]z[:\s]*([A-Za-z0-9_\s]+?)(?=\s*(?:lhNnf|uf=kf=|$|\n))',
                    r'Permanent.*?Province[:\s]*([A-Za-z0-9_\s]+)',
                    r'Province[:\s]*([A-Za-z0-9_\s]+?)(?=.*?District)',
                    r'(?:Province|k|b]z)[:\s]*([A-Za-z0-9_\s]+?)(?=\s*(?:District|lhNnf|Municipality|uf=kf=))'
                ],
                'district': [
                    r'Permanent Address[:\s]*.*?District[:\s]*([A-Za-z\s]+?)(?=\s*(?:Municipality|Ward|Tole|$|\n))',
                    r'Permanent.*?District[:\s]*([A-Za-z\s]+?)(?=\s*(?:Municipality|Ward|Tole|$|\n))',
                    r':yfoL 7]ufgf[:\s]*.*?lhNnf[:\s]*([A-Za-z\s]+?)(?=\s*(?:uf=kf=|j8f|6f]n|$|\n))',
                    r'Permanent.*?District[:\s]*([A-Za-z\s]+)',
                    r'District[:\s]*([A-Za-z\s]+?)(?=.*?Municipality)',
                    r'(?:District|lhNnf)[:\s]*([A-Za-z\s]+?)(?=\s*(?:Municipality|uf=kf=|Ward|j8f|Tole|6f]n))'
                ],
                'municipality': [
                    r'Permanent Address[:\s]*.*?Municipality[:\s]*([A-Za-z\s]+?)(?=\s*(?:Ward|Tole|Telephone|$|\n))',
                    r'Permanent.*?Municipality[:\s]*([A-Za-z\s]+?)(?=\s*(?:Ward|Tole|Telephone|$|\n))',
                    r':yfoL 7]ufgf[:\s]*.*?uf=kf=[:\s]*([A-Za-z\s]+?)(?=\s*(?:j8f|6f]n|6]lnkmf]g|$|\n))',
                    r'Permanent.*?Municipality[:\s]*([A-Za-z\s]+)',
                    r'Municipality[:\s]*([A-Za-z\s]+?)(?=.*?Ward)',
                    r'(?:Municipality|uf=kf=)[:\s]*([A-Za-z\s]+?)(?=\s*(?:Ward|j8f|Tole|6f]n|Telephone|6]lnkmf]g))'
                ],
                'ward_no': [
                    r'Permanent Address[:\s]*.*?Ward No[.:]?\s*(\d+)(?=\s*(?:Tole|Telephone|Block|$|\n))',
                    r'Permanent.*?Ward No[.:]?\s*(\d+)(?=\s*(?:Tole|Telephone|Block|$|\n))',
                    r'Permanent Ward Number[:\s]*(\d+)',
                    r':yfoL 7]ufgf[:\s]*.*?j8f g+=[:\s]*(\d+)(?=\s*(?:6f]n|6]lnkmf]g|$|\n))',
                    r'Permanent.*?Ward.*?(\d+)',
                    r'Ward No[.:]?\s*(\d+)',
                    r'Ward Number[:\s]*(\d+)',
                    r'(?:Ward|j8f)[:\s]*(?:No[.:]?\s*|Number[:\s]*|g+=[:\s]*)?(\d+)'
                ],
                'tole': [
                    r'Permanent Address[:\s]*.*?Tole[:\s]*([A-Za-z\s]+?)(?=\s*(?:Telephone|Block|$|\n))',
                    r'Permanent.*?Tole[:\s]*([A-Za-z\s]+?)(?=\s*(?:Telephone|Block|$|\n))',
                    r'Permanent Address Tole[:\s]*([A-Za-z\s]+)',
                    r':yfoL 7]ufgf[:\s]*.*?6f]n[:\s]*([A-Za-z\s]+?)(?=\s*(?:6]lnkmf]g|$|\n))',
                    r'Permanent.*?Tole[:\s]*([A-Za-z\s]+)',
                    r'Tole[:\s]*([A-Za-z\s]+?)(?=.*?Telephone)',
                    r'(?:Tole|6f]n)[:\s]*([A-Za-z\s]+?)(?=\s*(?:Telephone|6]lnkmf]g|Block|$|\n))'
                ],
                'telephone': [
                    r'Permanent Address[:\s]*.*?Telephone No[.:]?\s*(\d+)',
                    r'Permanent Telephone Number[:\s]*(\d+)',
                    r':yfoL 7]ufgf[:\s]*.*?6]lnkmf]g g+=[:\s]*(\d+)',
                    r'Permanent.*?Telephone.*?(\d+)',
                    r'Telephone No[.:]?\s*(\d+)',
                    r'Telephone Number[:\s]*(\d+)',
                    r'(?:Telephone|6]lnkmf]g)[:\s]*(?:No[.:]?\s*|Number[:\s]*|g+=[:\s]*)?(\d+)'
                ],
                'block_no': [
                    r'Permanent Address[:\s]*.*?Block No[.:]?\s*(\d+)',
                    r'Permanent Block Number[:\s]*(\d+)',
                    r':yfoL 7]ufgf[:\s]*.*?An]s g+=[:\s]*(\d+)',
                    r'Permanent.*?Block.*?(\d+)',
                    r'Block No[.:]?\s*(\d+)',
                    r'Block Number[:\s]*(\d+)',
                    r'(?:Block|An]s)[:\s]*(?:No[.:]?\s*|Number[:\s]*|g+=[:\s]*)?(\d+)'
                ]
            },
             'family_members': {
                    #gf and father different name woking
                 'grandfather_name': [
                    r'Grand\s*Father\'?s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Father\'?s?\s*Name|Father\s*Name|\n|$))',
                    r'Grandfather\'?s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Father\'?s?\s*Name|Father\s*Name|\n|$))',
                    r'Grand\s*Father[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Father\'?s?\s*Name|Father\s*Name|\n|$))',
                    r'(?:Grand\s*Father|Grandfather)\'?s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Father\'?s?\s*Name|Father\s*Name|\n|$))'
                ],

                'father_name': [
                    r'(?<!Grand\s)(?<!Grandfather\s)Father\'?s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Mother\'?s?\s*Name|Spouse\'?s?\s*Name|Son\'?s?\s*Name|Daughter\'?s?\s*Name|$|\n))',
                    r'(?<!Grand\s)(?<!Grandfather\s)Father[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Name|Mother\'?s?\s*Name|Spouse\'?s?\s*Name|Son\'?s?\s*Name|Daughter\'?s?\s*Name|$|\n))'
                ],

                 
            'mother_name': [
                r'Mother\'?s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Spouse|Son|Daughter|$|\n))',
                r'cfdfsf\]\s*gfd[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:klt÷kTgLsf\]|5f\]/fsf\]|$|\n))'
            ],
            'spouse_name': [
                r'Spouse\'?s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Son|Daughter|Bank|$|\n))',
                r'klt÷kTgLsf\]\s*gfd[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:5f\]/fsf\]|5f\]/Lsf\]|$|\n))'
            ],
            'son_name': [
                r'Son\'?s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Daughter|Bank|Details|$|\n))',
                r'5f\]/fsf\]\s*gfd[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:5f\]/Lsf\]|a\}+s|$|\n))'
            ],
            'daughter_name': [
                r'daughters?\s*name[:\s]*([A-Z][A-Z\s]+?)(?i)(?=\s*(?:Bank|Details|Money|$|\n))',
                r'Daughter\'s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Bank|Details|Money|in.*law|$|\n))',
                r'Daughter\'?s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Bank|Details|Money|$|\n))',
                r'5f\]/Lsf\]\s*gfd[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:a\}+s|k\}zf|$|\n))'
            ],
            'daughter_in_law_name': [
                r'Daughter\s*[-]?\s*in\s*[-]?\s*Law\'s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Father|Mother|Bank|Details|$|\n))',
                r'a\'xf/Lsf\]\s*gfd[:\s]*([A-Z][A-Z\s]+)',
                r'Daughter\s*[-]?\s*in\s*[-]?\s*law\'s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Father|Mother|Bank|Details|$|\n))',
                r'daughters?\s*in\s*law[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Father|Mother|Bank|Details|$|\n))',
                r'Daughter-in-law\'s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Father|Mother|Bank|Details|$|\n))',
                r'daughter\s*in\s*law\s*name[:\s]*([A-Z][A-Z\s]+?)(?i)',
                r'Daughter\s*[-]?in\s*[-]?law[:\s]*([A-Z][A-Z\s]+)'
            ],
            'father_in_law_name': [
                r'Father\s*in\s*Law\'?s?\s*Name[:\s]*([A-Z][A-Z\s]+)',
                r'Father\s*[-]?\s*in\s*[-]?\s*Law\'s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Mother|Bank|Details|$|\n))',
                r'Father\s*[-]?in\s*[-]?law[:\s]*([A-Z][A-Z\s]+)',
                r'Father\s*[-]?\s*in\s*[-]?\s*law\'s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Mother|Bank|Details|$|\n))',
                r'Father-in-law\'s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Mother|Bank|Details|$|\n))',
                r'father\s*in\s*law\s*name[:\s]*([A-Z][A-Z\s]+?)(?i)'
            ],
            'mother_in_law_name': [
                r'Mother\s*in\s*Law\'?s?\s*Name[:\s]*([A-Z][A-Z\s]+)',
                r'Mother\s*[-]?\s*in\s*[-]?\s*Law\'s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Bank|Details|Occupation|$|\n))',
                r'Mother\s*[-]?in\s*[-]?law[:\gs]*([A-Z][A-Z\s]+)',
                r'Mother\s*[-]?\s*in\s*[-]?\s*law\'s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Bank|Details|Occupation|$|\n))',
                r'Mother-in-law\'s?\s*Name[:\s]*([A-Z][A-Z\s]+?)(?=\s*(?:Bank|Details|Occupation|$|\n))',
                r'mother\s*in\s*law\s*name[:\s]*([A-Z][A-Z\s]+?)(?i)'
            ]
            },
            'bank_details': {
                'account_type': [
                    r'Type of Bank Account[:\s]+(Saving|Current)(?=\s*(?:Bank Account|Name|Details|$|\n))',
                    r'a}+s vftfsf] lsl;d[:\s]+(art|rNtL)(?=\s*(?:a}+s vftf|gfd|$|\n))'
                ],
                'account_number': [
                    r'Bank Account Number[:\s]+(\d+)(?=\s*(?:Name & Address|Bank|Details|$|\n))',
                    r'a}+s vftf gDa/[:\s]+(\d+)(?=\s*(?:a}+s.*?gfd|$|\n))'
                ],
                'bank_name': [
                    r'Name & Address of Bank[:\s]+([A-Za-z\s,]+?)(?=\s*(?:Details of Occupation|Occupation|Agreement|$|\n))',
                    r'a}+s.*?gfd[:\s]+([A-Za-z\s,]+?)(?=\s*(?:k]zfut|ljj/0f|$|\n))'
                ]
            },
            'occupation': {
                # 'occupation': [
                #     r'Details of Occupation\s+Occupation\s+([A-Za-z]+)',
                #     r'Occupation\s+([A-Za-z]+)(?=\s*(?:Types|Organization|Name|$|\n))',
                #     r'k]zf[:\s]+([A-Za-z]+)(?=\s*(?:k|sf/|;+:yf|$|\n))'
                # ],
                 'occupation': [
                        r'Occupation[\s\n]*([A-Za-z/ ]{3,50})(?=\s*(?:Types|Organization|Name|$|\n))',
                        r'Details of Occupation[\s\n]*Occupation[\s\n]*([A-Za-z/ ]{3,50})',
                        r'k]zf[:\s\n]*([A-Za-z/ ]{3,50})(?=\s*(?:k|sf/|;+:yf|$|\n))'
                    ],
                #occupation organization name
            'organization_name': [
                    r"Organization'?s?[\s\n]*Name[\s\n]*((?:[A-Z0-9 ,\-&]{2,}(?:\n| ){0,2}){1,5})"
                ],
                'organization': [
                    r'Organization\'s Name[:\s]+([A-Za-z\s\-]+?)(?=\s*(?:Address|Designation|$|\n))',
                    r';+:yfsf] gfd[:\s]+([A-Za-z\s\-]+?)(?=\s*(?:7]ufgf|kb|$|\n))'
                ],
                # 'designation': [
                #     r'Designation[:\s]+([A-Za-z\s\-]+?)(?=\s*(?:ID No|Employee|$|\n))',
                #     r'kb[:\s]+([A-Za-z\s\-]+?)(?=\s*(?:sd{rf/L|k|lr/rokq|$|\n))'
                # ],
       
                'designation': [
                    r'Designation[\s]+([A-Za-z\s\-]{2,50})(?=\s*(ID No|Employee|Number|$|\n))',
                    r'kb[\s]+([A-Za-z\s\-]{2,50})(?=\s*(sd{rf/L|k|lr/rokq|$|\n))'
                ],

                 'sector': [
                    r'Occupation\s*[:\s]*([^\n]+)'
                ],
             'address': [
                    r'Address[\s\n]*([A-Z0-9 ,\-]{3,50})'
                ],

                'financial_details': [
                    r'Income Limit\(Annual Details\)\s*([^\n]+)'
                ],
                # 'investment_involvement': [
                #     r'Involvement in Investment companies which were established for securities trading\s*([^\n]+)'
                # ]
                
                'investment_involvement': [
                    r'Involvement in Investment companies which were established for securities trading\s*(Yes|No)'
                ],
                'business_type': [
                    r'Types of[\s\n]*Business[\s\n]*([A-Za-z ]+)',
                    r'Service Oriented[\s\n]*([A-Za-z ]+)',
                    r'Manufacturing[\s\n]*([A-Za-z ]+)',
                    r'Others[\s\n]*([A-Za-z ]+)'
                ],

            },
            'money_laundering': {
                'politician_or_high_ranking_person': [
                    r'Are You A Politician Or A High-Ranking Person\?\s*(Yes|No)'
                ],
                'related_to_politician_or_high_ranking_official': [
                    r'Are You Related To A Politician Or A High-Ranking Official\?\s*(Yes|No)'
                ],
                'have_a_beneficiary': [
                    r'Do You Have A Beneficiary\?\s*(Yes|No)'
                ],
                'convicted_of_felony': [
                    r'Have You Been Convicted Of A Felony In The Past\?\s*(Yes|No)'
                ]
            },
            'guardian_details': {
                'guardian_name': [
                    r"Name/Surname[\s:]+([A-Z\s]{3,20})(?=\s+Relationship|$)"
                ],
                'guardian_relationship': [
                    r"Relationship with[\s]+applicant[\s:]+([A-Z\s]{3,15})(?=\s+Correspondence|Address|$)"
                ]
            },
            'minor_contact': {
                'minor_telephone': [
                    r'Telephone\s+No[:\s]+([0-9]{6,15})'
                ],
                'minor_mobile': [
                    r'Mobile\s+No[:\s]+([0-9]{6,15})'
                ]
            },


            'temporary_address': {
                'country': [
                    r'Temporary Address[:\s]*.*?Country[:\s]*([A-Za-z\s]+)',
                    r'c:yfoL 7]ufgf[:\s]*.*?b]z[:\s]*([A-Za-z\s]+)'
                ],
                'province': [
                    r'Temporary Address[:\s]*.*?Province[:\s]*([A-Za-z0-9_\s]+)',
                    r'c:yfoL 7]ufgf[:\s]*.*?k|b]z[:\s]*([A-Za-z0-9_\s]+)'
                ],
                'district': [
                    r'Temporary Address[:\s]*.*?District[:\s]*([A-Za-z\s]+)',
                    r'c:yfoL 7]ufgf[:\s]*.*?lhNnf[:\s]*([A-Za-z\s]+)'
                ],
                'municipality': [
                    r'Temporary Address[:\s]*.*?Municipality[:\s]*([A-Za-z\s]+)',
                    r'c:yfoL 7]ufgf[:\s]*.*?uf=kf=[:\s]*([A-Za-z\s]+)'
                ],
                'ward_no': [
                    r'Temporary Address[:\s]*.*?Ward No[.:]?\s*(\d+)',
                    r'c:yfoL 7]ufgf[:\s]*.*?j8f g+=[:\s]*(\d+)'
                ],
                'tole': [
                    r'Temporary Address[:\s]*.*?Tole[:\s]*([A-Za-z\s]+)',
                    r'c:yfoL 7]ufgf[:\s]*.*?6f]n[:\s]*([A-Za-z\s]+)'
                ],
                'telephone': [
                    r'Temporary Address[:\s]*.*?Telephone No[.:]?\s*(\d+)',
                    r'c:yfoL 7]ufgf[:\s]*.*?6]lnkmf]g g+=[:\s]*(\d+)'
                ],
                'mobile': [
                    r'Temporary Address[:\s]*.*?Mobile No[.:]?\s*(\d+)',
                    r'c:yfoL 7]ufgf[:\s]*.*?df]afOn g+=[:\s]*(\d+)'
                ],
                'email': [
                    r'Temporary Address[:\s]*.*?Email ID[:\s]*([A-Za-z0-9@._\-]+)',
                    r'c:yfoL 7]ufgf[:\s]*.*?O{d]n[:\s]*([A-Za-z0-9@._\-]+)'
                ]
            },
            'financial_details': {
                'income_limit': [
                    r'Income Limit\s*\(Annual Details\)\s*([A-Za-z0-9,\s\-\.]+?)(?=\s*(?:Involvement|Details|Bank|$|\n))',
                    r'Income Limit[:\s]*([A-Za-z0-9,\s\-\.]+?)(?=\s*(?:Details|Bank|$|\n))',
                    r'Financial Details[:\s]*([A-Za-z0-9,\s\-\.]+?)(?=\s*(?:Bank|Agreement|$|\n))',
                    r'jflifs[:\s]*([A-Za-z0-9,\s\-\.]+)',
                    r'cfly[:\s]*([A-Za-z0-9,\s\-\.]+)'
                ],
                'annual_income': [
                    r'Annual Income[:\s]*([A-Za-z0-9,\s\-\.]+?)(?=\s*(?:Details|Bank|$|\n))',
                    r'jflifs cfo[:\s]*([A-Za-z0-9,\s\-\.]+)'
                ]
            }
        }
    
    def parse_data(self, text: str) -> Dict:
        """
        Parse extracted text to identify and extract relevant data fields
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            dict: Parsed data with field names as keys
        """
        if not text:
            return {}
        
        parsed_data = {}
        
        try:
            # Extract basic personal information
            parsed_data.update(self._extract_basic_info(text))
            
            # Extract address information
            parsed_data.update(self._extract_address_info(text))
            
            
            # Extract bank details
            parsed_data.update(self._extract_bank_info(text))
            
            # Extract occupation details
            parsed_data.update(self._extract_occupation_info(text))

            # Extract guardian details 
            parsed_data.update(self._extract_guardian_info(text))

            # Extract minor contact details
            parsed_data.update(self._extract_minor_contact_info(text))


            # Extract temporary address
            parsed_data.update(self._extract_temporary_address_info(text))
            
            # Extract financial details
            parsed_data.update(self._extract_financial_info(text))

             # Extract family member information with validation
            family_data = self._extract_family_info(text)
            parsed_data.update(self._validate_family_names(family_data))

            # Extract money laundering questions
            parsed_data.update(self._extract_money_laundering_info(text))
            
            return parsed_data
            
        except Exception as e:
            st.error(f"Error parsing data: {str(e)}")
            return {}

    def _extract_family_info(self, text: str) -> Dict:
        """Extract family member information with improved accuracy"""
        data = {}
        
        # Extract each family member with ordered priority
        members = [
            'grandfather_name',
            'father_name', 
            'mother_name',
            'spouse_name',
            'son_name',
            'daughter_name',
            'daughter_in_law_name',
            'father_in_law_name',
            'mother_in_law_name'
        ]
        
        for member in members:
            value = self._extract_field(text, self.patterns['family_members'][member])
            if value:
                # Clean and standardize the name
                cleaned_value = ' '.join(value.strip().upper().split())
                if cleaned_value and cleaned_value != '-':
                    data[member] = cleaned_value
        
        return data

    
    def _extract_basic_info(self, text: str) -> Dict:
        """Extract basic personal information"""
        data = {}
        
        # Extract name
        name = self._extract_field(text, self.patterns['name'])
        if name:
            # Ensure name is fully capitalized
            data['name'] = name.strip().upper()
        
        # Extract date of birth
        dob = self._extract_field(text, self.patterns['date_of_birth'])
        if dob:
            data['date_of_birth'] = dob.strip()
        
        # Extract gender
        gender = self._extract_field(text, self.patterns['gender'])
        if gender:
            # Normalize gender
            gender_normalized = gender.upper()
            if gender_normalized in ['M', 'MALE', 'k\w*if']:
                data['gender'] = 'Male'
            elif gender_normalized in ['F', 'FEMALE', 'dlxnf']:
                data['gender'] = 'Female'
            else:
                data['gender'] = gender.strip()
        
        # Extract citizenship number
        citizenship = self._extract_field(text, self.patterns['citizenship_no'])
        if citizenship:
            # Clean and validate citizenship number
            citizenship_clean = citizenship.strip()
            # Remove any extra characters and keep only numbers, hyphens, and slashes
            citizenship_clean = re.sub(r'[^\d\-/]', '', citizenship_clean)
            
            # Additional validation to avoid dates (typically 4-digit years)
            if (citizenship_clean and len(citizenship_clean) >= 3 and 
                not re.match(r'^\d{4}[-/]\d{2}[-/]\d{2}$', citizenship_clean) and  # Not a date format
                not citizenship_clean.startswith('20') and  # Not starting with year 20xx
                not citizenship_clean.startswith('19')):   # Not starting with year 19xx
                data['citizenship_no'] = citizenship_clean
        
        # Extract beneficiary ID
        beneficiary_id = self._extract_field(text, self.patterns['beneficiary_id'])
        if beneficiary_id:
            # Clean beneficiary ID - keep only numbers
            beneficiary_clean = re.sub(r'[^\d]', '', beneficiary_id.strip())
            if beneficiary_clean and len(beneficiary_clean) >= 1:
                data['beneficiary_id'] = beneficiary_clean
        
        # Extract PAN number (only if it's a valid PAN format)
        pan = self._extract_field(text, self.patterns['pan_no'])
        if pan and pan.strip() != '-' and not pan.lower().endswith('ies'):
            # Validate PAN format (should be alphanumeric, 9-12 characters)
            pan_clean = pan.strip()
            if len(pan_clean) >= 9 and pan_clean.replace('-', '').isalnum():
                data['pan_no'] = pan_clean
        
        # Extract National ID number
        national_id = self._extract_field(text, self.patterns['national_id'])
        if national_id and national_id.strip() != '-':
            data['national_id'] = national_id.strip()
        
        # Extract issue district and date
        issue_district = self._extract_field(text, self.patterns['issue_district'])
        if issue_district and issue_district.strip() != '-':
            data['issue_district'] = issue_district.strip()
            
        issue_date = self._extract_field(text, self.patterns['issue_date'])
        if issue_date and issue_date.strip() != '-':
            data['issue_date'] = issue_date.strip()
        
        return data
    
    def _extract_address_info(self, text: str) -> Dict:
        """Extract address information with better separation between current and permanent"""
        data = {}

        # Split text into sections to better separate current and permanent addresses
        text_lines = text.split('\n')
        current_section = []
        permanent_section = []

        in_current = False
        in_permanent = False

        for line in text_lines:
            line_lower = line.lower().strip()

            # Detect current address section
            if 'current address' in line_lower and 'permanent' not in line_lower:
                in_current = True
                in_permanent = False
                current_section.append(line)
                continue

            # Detect permanent address section  
            if 'permanent address' in line_lower:
                in_permanent = True
                in_current = False
                permanent_section.append(line)
                continue

            # Add lines to appropriate section
            if in_current and not in_permanent:
                current_section.append(line)
                # Stop current section if we hit certain keywords
                if any(keyword in line_lower for keyword in ['permanent', 'temporary', 'family', 'bank', 'occupation']):
                    in_current = False
            elif in_permanent and not in_current:
                permanent_section.append(line)
                # Stop permanent section if we hit certain keywords
                if any(keyword in line_lower for keyword in ['temporary', 'family', 'bank', 'occupation']):
                    in_permanent = False

        current_text = '\n'.join(current_section)
        permanent_text = '\n'.join(permanent_section)

        # Extract current address from current section
        for field, patterns in self.patterns['current_address'].items():
            value = self._extract_field(current_text, patterns)
            if not value:
                # Fallback to original text but with stricter patterns
                value = self._extract_field(text, patterns)
            if value and value.strip() and value.strip() != '-':
                data[f'current_{field}'] = value.strip()

        # Extract permanent address from permanent section
        for field, patterns in self.patterns['permanent_address'].items():
            value = self._extract_field(permanent_text, patterns)
            if not value:
                # Fallback to original text
                value = self._extract_field(text, patterns)
            if value and value.strip() and value.strip() != '-':
                # Clean up the value to remove extra text
                clean_value = value.strip()

                # More comprehensive cleaning
                if field == 'country':
                    if 'Province' in clean_value:
                        clean_value = clean_value.split('Province')[0].strip()
                    if 'District' in clean_value:
                        clean_value = clean_value.split('District')[0].strip()
                elif field == 'province':
                    if 'District' in clean_value:
                        clean_value = clean_value.split('District')[0].strip()
                    if 'Municipality' in clean_value:
                        clean_value = clean_value.split('Municipality')[0].strip()
                elif field == 'district':
                    if 'Municipality' in clean_value:
                        clean_value = clean_value.split('Municipality')[0].strip()
                    if 'Ward' in clean_value:
                        clean_value = clean_value.split('Ward')[0].strip()
                elif field == 'municipality':
                    if 'Ward' in clean_value:
                        clean_value = clean_value.split('Ward')[0].strip()
                    if 'Tole' in clean_value:
                        clean_value = clean_value.split('Tole')[0].strip()

                # Remove any remaining unwanted characters
                clean_value = re.sub(r'[:\s]+$', '', clean_value)
                clean_value = re.sub(r'^[:\s]+', '', clean_value)

                if clean_value and clean_value != '-':
                    data[f'permanent_{field}'] = clean_value

        return data
    
    # def _extract_family_info(self, text: str) -> Dict:
    #     """Extract family member information"""
    #     data = {}
        
    #     for field, patterns in self.patterns['family_members'].items():
    #         value = self._extract_field(text, patterns)
    #         if value and value.strip() and value.strip() != '-':
    #             # Ensure family member names are fully capitalized
    #             data[field] = value.strip().upper()
        
    #     return data

    def _extract_family_info(self, text: str) -> Dict:
        """Extract family member information with improved accuracy"""
        data = {}

        members = [
            'grandfather_name', 'father_name', 'mother_name',
            'spouse_name', 'son_name', 'daughter_name',
            'daughter_in_law_name', 'father_in_law_name', 'mother_in_law_name'
        ]

        for member in members:
            value = self._extract_field(text, self.patterns['family_members'][member])
            if value:
                cleaned = value.strip().upper()
                # Reject values that are just field labels
                label_words = member.replace('_name', '').replace('_', ' ').upper()
                if cleaned == label_words or cleaned in ['DAUGHTER', 'SON', 'MOTHER', 'FATHER', 'MONEY LAUNDERING']:
                    continue
                if cleaned and cleaned != '-':
                    data[member] = cleaned

        return data


    
    def _extract_bank_info(self, text: str) -> Dict:
        """Extract bank account information"""
        data = {}
        
        for field, patterns in self.patterns['bank_details'].items():
            value = self._extract_field(text, patterns)
            if value and value.strip() and value.strip() != '-':
                # Clean up the field name - remove 'bank_' prefix for bank_name to avoid double prefix
                if field == 'bank_name':
                    data['bank_name'] = value.strip()
                else:
                    data[f'bank_{field}'] = value.strip()
        
        return data
       
    def _validate_family_names(self, family_data: Dict) -> Dict:
        """Ensure family member names are distinct and valid"""
        validated = {}
        
        # Father and grandfather shouldn't be same
        if 'father_name' in family_data and 'grandfather_name' in family_data:
            if family_data['father_name'] == family_data['grandfather_name']:
                st.warning("Father and grandfather names are identical - likely extraction error")
                # del family_data['grandfather_name']
        
        # Spouse shouldn't match parent names
        if 'spouse_name' in family_data:
            if 'father_name' in family_data and family_data['spouse_name'] == family_data['father_name']:
                del family_data['spouse_name']
            if 'mother_name' in family_data and family_data['spouse_name'] == family_data['mother_name']:
                del family_data['spouse_name']
    
        return family_data

    # def _extract_occupation_info(self, text: str) -> Dict:
    #     """Extract occupation information"""
    #     data = {}
        
    #     for field, patterns in self.patterns['occupation'].items():
    #         value = self._extract_field(text, patterns)
    #         if value and value.strip() and value.strip() != '-':
    #             data[field] = value.strip()
        
    #     return data
    
    # def _extract_occupation_info(self, text: str) -> Dict:
    #     """Extract occupation information"""
    #     data = {}
        
    #     for field, patterns in self.patterns['occupation'].items():
    #             value = self._extract_field(text, patterns)

    #             if value:
    #                 # Clean extraneous label spillover
    #                 value = re.split(r'\b(Address|Designation|ID No)\b', value)[0]
    #                 value = re.sub(r'\s+', ' ', value.strip())
            
    #             if value and value != '-':
    #                 lower_val = value.lower()
    #                 # Reject known layout artifacts
    #                 if lower_val in ['permanent', 'current', 'temporary', 'occupation', 'address']:
    #                     continue
    #                 # Reject exact label repetition
    #                 field_label = field.replace('_name', '').replace('_', ' ').strip().lower()
    #                 if lower_val == field_label:
    #                     continue
    #                 data[field] = value  
                    
    #     return data
    
    def _extract_occupation_info(self, text: str) -> Dict:
        """Extract occupation information"""
        data = {}

        for field, patterns in self.patterns['occupation'].items():
            value = self._extract_field(text, patterns)

            if value:
                # Clean extraneous label spillover
                value = re.split(r'\b(Address|Designation|ID No)\b', value)[0]
                value = re.sub(r'\s+', ' ', value.strip())

            # if value and value != '-':
            #     # Skip junk label
            #     if field == 'occupation' and value.lower() == 'occupation':
            #         continue
            #     data[field] = value
                
            if value and value != '-':
                lower_val = value.lower()
                # Reject known layout artifacts
                if lower_val in ['permanent', 'current', 'temporary', 'occupation', 'address']:
                    continue
                # Reject exact label repetition
                field_label = field.replace('_name', '').replace('_', ' ').strip().lower()
                if lower_val == field_label:
                    continue
                data[field] = value    

        # Fallback if occupation is missing
        if 'occupation' not in data and 'sector' in data:
            data['occupation'] = data['sector']

        return data
  
    def _extract_guardian_info(self, text: str) -> Dict:
        """Extract guardian information for minor applicants"""
        data = {}

        for field, patterns in self.patterns['guardian_details'].items():
            value = self._extract_field(text, patterns)
            if value and value.strip() and value.strip() != '-':
                data[field] = re.sub(r'\s+', ' ', value.strip())

        return data
    def _extract_minor_contact_info(self, text: str) -> Dict:
        """Extract minor's contact info"""
        data = {}

        for field, patterns in self.patterns['minor_contact'].items():
            value = self._extract_field(text, patterns)
            if value and value.strip() and value.strip() != '-':
                data[field] = re.sub(r'\s+', '', value.strip())  # remove inner spaces

        return data



    def _extract_temporary_address_info(self, text: str) -> Dict:
        """Extract temporary address information"""
        data = {}
        
        for field, patterns in self.patterns['temporary_address'].items():
            value = self._extract_field(text, patterns)
            if value and value.strip() and value.strip() != '-':
                # Clean up the value to remove extra text
                clean_value = value.strip()
                if field == 'country' and 'Province' in clean_value:
                    clean_value = clean_value.split('Province')[0].strip()
                data[f'temporary_{field}'] = clean_value
        
        return data
    
    def _extract_money_laundering_info(self, text: str) -> Dict:
            """Extract money laundering information"""
            data = {}
            for field, patterns in self.patterns['money_laundering'].items():
                value = self._extract_field(text, patterns)
                if value and value.strip() and value.strip() != '-':
                  data[field] = value.strip()
            return data 
    
    def _extract_financial_info(self, text: str) -> Dict:
        """Extract financial information"""
        data = {}
        
        for field, patterns in self.patterns['financial_details'].items():
            value = self._extract_field(text, patterns)
            if value and value.strip() and value.strip() != '-':
                data[field] = value.strip()
        
        return data
    
    def _extract_field(self, text: str, patterns: List[str]) -> Optional[str]:
        """
        Extract field using multiple regex patterns
        
        Args:
            text: Text to search in
            patterns: List of regex patterns to try
            
        Returns:
            str or None: Extracted value or None if not found
        """
        for pattern in patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    extracted_value = match.group(1).strip()
                    if extracted_value and extracted_value != '-':
                        return extracted_value
            except Exception:
                continue
        
        return None
    
    def get_extraction_summary(self, parsed_data: Dict) -> Dict:
        """
        Generate a summary of extracted data
        
        Args:
            parsed_data: Parsed data dictionary
            
        Returns:
            dict: Summary statistics
        """
        summary = {
            'total_fields': len(parsed_data),
            'filled_fields': len([v for v in parsed_data.values() if v and str(v).strip()]),
            'empty_fields': len([v for v in parsed_data.values() if not v or not str(v).strip()]),
            'categories': {
                'personal_info': 0,
                'address_info': 0,
                'family_info': 0,
                'bank_info': 0,
                'occupation_info': 0
            }
        }
        
        # Categorize fields
        for key in parsed_data.keys():
            if key in ['name', 'date_of_birth', 'gender', 'citizenship_no', 'beneficiary_id', 'pan_no']:
                summary['categories']['personal_info'] += 1
            elif key.startswith('current_'):
                summary['categories']['address_info'] += 1
            elif key.endswith('_name') and 'father' in key or 'mother' in key or 'spouse' in key:
                summary['categories']['family_info'] += 1
            elif key.startswith('bank_'):
                summary['categories']['bank_info'] += 1
            elif key in ['occupation', 'organization', 'designation']:
                summary['categories']['occupation_info'] += 1
        
        return summary
