import datetime as dt
from datetime import datetime

import requests
from fastapi import HTTPException
from scripts.config import Auth, ProjectConf
from scripts.core.constants.api import APIEndpoints
from scripts.core.constants.app_constants import AppConstants
from scripts.core.schemas.request_response import (
    DefaultFailureResponse,
    DefaultSuccessResponse,
)
from scripts.logging import logger
from scripts.utils.security_utils.jwt_util import JWT


class DateFilter:
    def __init__(self, user_id=None, payload=None):
        self.input_payload = payload
        self.user_id = user_id

    def get_fy_qp_filter(self):
        try:
            response = DefaultSuccessResponse().dict()
            p_results = self.get_period()
            if p_results:
                response["message"] = "Data Fetched Successfully"
                q_results = []
                count = 1
                for i in range(0, len(p_results), 3):
                    each_quater = p_results[i : i + 3]
                    q_results.append(
                        {
                            "label": "Q" + str(count),
                            "value": [
                                each_quater[0]["value"][0],
                                each_quater[-1]["value"][-1],
                            ],
                        }
                    )
                    count += 1
                result_json = {"quarters": q_results, "period": p_results}
                response["data"] = result_json
            return response
        except Exception as users_error:
            logger.error(f"Error in list_lookup {users_error}")
            return DefaultFailureResponse().dict()

    def get_fy_filter(self):
        try:
            response = DefaultSuccessResponse().dict()
            lookup_details = self.list_lookup()
            lookup_name = ProjectConf.fy_lookup_name
            actual_lookup_details = None
            for each_item in lookup_details:
                if lookup_name.lower() == each_item["lookup_name"].lower():
                    details_list = self.get_lookup_details(
                        each_item["lookup_id"], each_item["lookup_name"]
                    )
                    actual_lookup_details = details_list
                    break
            if actual_lookup_details:
                response["message"] = "Data Fetched Successfully"
                result_list = []
                for each_row in actual_lookup_details:
                    if str(each_row["status"]).lower() == "active":
                        sd = datetime.strftime(
                            datetime.strptime(
                                each_row["startTime"], AppConstants.datetimeformate1
                            ),
                            AppConstants.datetimeformate,
                        )
                        try:
                            ed = datetime.strftime(
                                datetime.strptime(
                                    each_row["endTime"], AppConstants.datetimeformate1
                                ),
                                AppConstants.datetimeformate,
                            )
                        except Exception as e:
                            logger.error(f"Error in time conversion {e}")
                            ed = datetime.strftime(
                                datetime.strptime(
                                    each_row["endTime"], AppConstants.datetimeformate2
                                ),
                                AppConstants.datetimeformate,
                            )
                        result_list.append(
                            {"label": each_row["lookupdata_id"], "value": [sd, ed]}
                        )
                result_list = sorted(
                    result_list, key=lambda d: d["label"], reverse=True
                )
                result_json = {"financial_years": result_list}
                response["data"] = result_json
            return response
        except Exception as users_error:
            logger.error(f"Error in list_lookup {users_error}")
            return DefaultFailureResponse().dict()

    def list_lookup(self):
        try:
            payload = {
                "project_id": self.input_payload.get("project_id"),
                "project_type": self.input_payload.get(
                    "project_type", "n_level_hierarchy"
                ),
                "tz": self.input_payload.get("tz", "Asia/Kolkata"),
                "language": self.input_payload.get("language", "en"),
            }

            url = f"{Auth.host_name}{APIEndpoints.list_lookup}"
            headers = {"Content-Type": "application/json"}
            cookies = {"login-token": ProjectConf.access_token}

            if str(ProjectConf.encrypt_payload).lower() == "true":
                payload = JWT().encode(payload=payload)
                response = requests.post(
                    url, data=payload, headers=headers, cookies=cookies
                )
            else:
                response = requests.post(
                    url, json=payload, headers=headers, cookies=cookies
                )
            if response.status_code != 200:
                msg = "Failed to list lookup " + str(response)
                logger.info("response---> " + str(response))
                logger.info("response status code---> " + str(response.status_code))
                raise HTTPException(status_code=response.status_code, detail=msg)

            response = response.json()
            lookup_data = (
                response.get("data", {}).get("tableData", {}).get("bodyContent", [])
            )
            return lookup_data
        except Exception as lookup_error:
            logger.error(f"Error in list_lookup {lookup_error}")

    def get_lookup_details(self, lookup_id, lookup_name):
        try:
            payload = {
                "lookup_id": lookup_id,
                "lookup_name": lookup_name,
                "project_id": self.input_payload.get("project_id"),
                "project_type": self.input_payload.get(
                    "project_type", "n_level_hierarchy"
                ),
                "tz": self.input_payload.get("tz", "Asia/Kolkata"),
                "language": self.input_payload.get("language", "en"),
            }

            url = f"{Auth.host_name}{APIEndpoints.get_lookup_details}"
            headers = {"Content-Type": "application/json"}
            cookies = {"login-token": ProjectConf.access_token}

            if str(ProjectConf.encrypt_payload).lower() == "true":
                payload = JWT().encode(payload=payload)
                response = requests.post(
                    url, data=payload, headers=headers, cookies=cookies
                )
            else:
                response = requests.post(
                    url, json=payload, headers=headers, cookies=cookies
                )
            if response.status_code != 200:
                msg = "Failed to get lookup details " + str(response)
                logger.info("response---> " + str(response))
                logger.info("response status code---> " + str(response.status_code))
                raise HTTPException(status_code=response.status_code, detail=msg)

            response = response.json()
            lookup_data = response.get("data", {}).get("lookup_data", {})
            return lookup_data
        except Exception as lookup_error:
            logger.error(f"Error in get_lookup_details {lookup_error}")

    def get_period(self):
        try:
            startdate = self.input_payload["startdate"]
            enddate = self.input_payload["enddate"]
            period_lookup_name = str(ProjectConf.period_lookup_name)
            lookup_details = self.list_lookup()
            actual_lookup_details = None
            for each_item in lookup_details:
                if period_lookup_name.lower() == each_item["lookup_name"].lower():
                    details_list = self.get_lookup_details(
                        each_item["lookup_id"], each_item["lookup_name"]
                    )
                    actual_lookup_details = details_list
                    break
            period_in_weeks = actual_lookup_details[0]["properties"][0]["value"]
            start_date = datetime.strptime(startdate, AppConstants.datetimeformate)
            end_date = datetime.strptime(enddate, AppConstants.datetimeformate)
            result_list = []
            new_sd = start_date
            no_of_weeks = period_in_weeks.split(",")
            for i in range(0, len(no_of_weeks)):
                new_ed = new_sd + dt.timedelta(days=int(no_of_weeks[i]) * 7 - 1)
                result_list.append(
                    {
                        "label": "P" + str(i + 1),
                        "value": [
                            datetime.strftime(new_sd, AppConstants.datetimeformate),
                            datetime.strftime(new_ed, AppConstants.datetimeformate),
                        ],
                    }
                )
                new_sd = new_ed + dt.timedelta(days=1)
            if end_date != new_ed:
                logger.info("actual end date and derived end date didnt matched")
                logger.info("end_date--->" + str(end_date))
                logger.info("derived_end_date--->" + str(new_ed))
            return result_list
        except Exception as period_error:
            logger.error(f"Error in get_period {period_error}")
