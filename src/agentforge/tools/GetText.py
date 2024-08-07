import os
import requests
import io
import pypdf


class GetText:
    def read_file(self, file_name_or_url: str) -> dict:
        """
        Reads text from a file or URL based on the given input.

        Parameters:
        file_name_or_url (str): The file name or URL to read from.

        Returns:
        dict: A dictionary containing 'status' (success or failure) and 'content' (text or error message).
        """
        try:
            if file_name_or_url.startswith('http://') or file_name_or_url.startswith('https://'):
                return self.read_from_url(file_name_or_url)
            else:
                if file_name_or_url.endswith('.pdf'):
                    return self.read_pdf(file_name_or_url)
                elif file_name_or_url.endswith('.txt') or file_name_or_url.endswith('.md'):
                    return self.read_txt(file_name_or_url)
                else:
                    return {"status": "failure", "content": "Unsupported file format - Use URL, PDF or TXT formats."}
        except Exception as e:
            return {"status": "failure", "content": str(e)}

    def read_pdf(self, filename: str) -> dict:
        """
        Reads text from a PDF file.

        Parameters:
        filename (str): The path to the PDF file.

        Returns:
        dict: A dictionary containing 'status' (success or failure) and 'content' (text or error message).
        """
        if not os.path.exists(filename):
            return {"status": "failure", "content": "File not found"}

        try:
            with open(filename, 'rb') as file:
                content = io.BytesIO(file.read())
                text = self.extract_text_from_pdf(content)
            return {"status": "success", "content": text['content']}
        except Exception as e:
            return {"status": "failure", "content": str(e)}

    @staticmethod
    def read_txt(filename: str) -> dict:
        """
        Reads text from a TXT file.

        Parameters:
        filename (str): The path to the TXT file.

        Returns:
        dict: A dictionary containing 'status' (success or failure) and 'content' (text or error message).
        """
        if not os.path.exists(filename):
            return {"status": "failure", "content": "File not found"}

        try:
            with open(filename, 'r', encoding='utf-8') as file:
                text = file.read()
            return {"status": "success", "content": text}
        except Exception as e:
            return {"status": "failure", "content": str(e)}

    def read_from_url(self, url: str) -> dict:
        """
        Reads text from a URL.

        Parameters:
        url (str): The URL to read from.

        Returns:
        dict: A dictionary containing 'status' (success or failure) and 'content' (text or error message).
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            if url.endswith('.pdf'):
                return self.extract_text_from_pdf(io.BytesIO(response.content))
            elif url.endswith('.txt'):
                return {"status": "success", "content": response.text}
            else:
                return {"status": "failure", "content": "Unsupported file format"}
        except requests.RequestException as e:
            return {"status": "failure", "content": str(e)}

    @staticmethod
    def extract_text_from_pdf(file_stream: io.BytesIO) -> dict:
        """
        Extracts text from a PDF file stream.

        Parameters:
        file_stream (io.BytesIO): The file stream of the PDF.

        Returns:
        dict: A dictionary containing 'status' (success or failure) and 'content' (text or error message).
        """
        try:
            text = ""
            reader = pypdf.PdfReader(file_stream)
            for page in reader.pages:
                text += page.extract_text()
            return {"status": "success", "content": text}
        except Exception as e:
            return {"status": "failure", "content": str(e)}


if __name__ == "__main__":
    gettext_instance = GetText()
    filename_or_url = 'Documents'  # Replace with your file path or URL
    file_content = gettext_instance.read_file(filename_or_url)
    print(file_content)


# import pypdf
# import requests
# import io
#
#
# class GetText:
#     def read_file(self, file_name_or_url):
#         if file_name_or_url.startswith('http://') or file_name_or_url.startswith('https://'):
#             return self.read_from_url(file_name_or_url)
#         else:
#             if file_name_or_url.endswith('.pdf'):
#                 return self.read_pdf(file_name_or_url)
#             elif file_name_or_url.endswith('.txt'):
#                 return self.read_txt(file_name_or_url)
#             else:
#                 return "Unsupported file format"
#
#     def read_pdf(self, filename):
#         with open(filename, 'rb') as file:
#             text = self.extract_text_from_pdf(file)
#         return text
#
#     @staticmethod
#     def read_txt(filename):
#         with open(filename, 'r', encoding='utf-8') as file:
#             return file.read()
#
#     def read_from_url(self, url):
#         response = requests.get(url)
#         if url.endswith('.pdf'):
#             return self.extract_text_from_pdf(io.BytesIO(response.content))
#         elif url.endswith('.txt'):
#             return response.text
#         else:
#             return "Unsupported file format"
#
#     @staticmethod
#     def extract_text_from_pdf(file_stream):
#         text = ""
#         reader = pypdf.PdfReader(file_stream)
#         for page in reader.pages:
#             text += page.extract_text()
#         return text