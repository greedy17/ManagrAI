class NylasAPIError(Exception):
    def __init__(self, error="Nylas API error"):
        self.message = error
        super().__init__(self.message)


# class GongAPIException:
#     def __init__(self, e, fn_name=None, retries=0):
#         self.error = e
#         self.error_class_name = e.__class__.__name__
#         self.status_code = e.args[0]["status_code"]
#         self.error = e.args[0]["error_param"]
#         self.fn_name = fn_name
#         self.retry_attempts = 0
#         self.raise_error()

#     def raise_error(self):
#         # if an invalid Basic auth is sent the response is still a 200 success
#         # instead we check data.json() which will return a JSONDecodeError
#         if self.status_code == 422:
#             logger.error(f"Gong API error: {self.error}")
#             raise InvalidRequest()
#         if self.status_code == 404:
#             raise InvalidRequest(self.error)
#         elif self.status_code == 403 or self.status_code == 401:
#             raise TokenExpired()
#         else:
#             raise ValidationError({"detail": {"message": self.error,}})
