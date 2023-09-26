class Parsing:
    @staticmethod
    def extract_metadata(data):
        # extract the 'metadatas' key from results
        return data['metadatas'][0][0]

    @staticmethod
    def extract_outermost_brackets(string):
        count = 0
        start_idx = None
        end_idx = None

        for idx, char in enumerate(string):
            if char == '{':
                count += 1
                if count == 1:
                    start_idx = idx
            elif char == '}':
                count -= 1
                if count == 0 and start_idx is not None:
                    end_idx = idx
                    break

        if start_idx is not None and end_idx is not None:
            return string[start_idx:end_idx + 1]
        else:
            return None

    @staticmethod
    def string_to_dictionary(string):
        from ast import literal_eval as leval
        try:
            return leval(string)
        except Exception as e:
            raise ValueError(f"\n\nError while building parsing string to dictionary: {e}")
