from rest_framework.renderers import JSONRenderer

class CustomErrorJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Retrieve the response object to check the status code
        response = renderer_context.get('response') if renderer_context else None
        
        # If it's an error status code and the data returned is a dictionary
        if response is not None and response.status_code >= 400 and isinstance(data, dict):
            error_message = None
            
            # 1. Look for standard error string keys ('message', 'detail', 'error')
            for key in ['message', 'detail', 'error']:
                if key in data:
                    val = data[key]
                    # DRF sometimes wraps details in lists e.g. {"detail": ["Not found."]}
                    if isinstance(val, list) and len(val) > 0:
                        error_message = str(val[0])
                    else:
                        error_message = str(val)
                    break
            
            # 2. If it wasn't a standard key, it's likely a form/model validation error
            # Example: {"email": ["This field is required."]}
            if error_message is None:
                for key, val in data.items():
                    # Format as 'field_name: Error message'
                    if isinstance(val, list) and len(val) > 0:
                        error_message = f"{key}: {val[0]}"
                    elif isinstance(val, str):
                        error_message = f"{key}: {val}"
                    else:
                        error_message = f"{key}: Invalid input."
                    break # Stop after finding the first error to keep it simple
            
            # 3. Fallback message if for some reason the dict was empty
            if error_message is None:
                error_message = "An unexpected error occurred."
                
            # Completely overwrite the output data payload
            data = {"message": error_message}
            
        # Delegate the actual JSON rendering back to the parent class
        return super().render(data, accepted_media_type, renderer_context)
