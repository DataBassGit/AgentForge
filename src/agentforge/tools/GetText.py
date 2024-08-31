import os
import requests
import io
import pypdf


class GetText:
    def read_file(self, file_name_or_url: str) -> str:
        """
        Reads text from a file or URL based on the given input.

        Parameters:
        file_name_or_url (str): The file name or URL to read from.

        Returns:
        str: The text content of the file or URL.

        Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is unsupported or if any error occurs.
        """
        if file_name_or_url.startswith('http://') or file_name_or_url.startswith('https://'):
            return self.read_from_url(file_name_or_url)
        else:
            if file_name_or_url.endswith('.pdf'):
                return self.read_pdf(file_name_or_url)
            elif file_name_or_url.endswith('.txt') or file_name_or_url.endswith('.md'):
                return self.read_txt(file_name_or_url)
            else:
                raise ValueError("Unsupported file format - Use URL, PDF, TXT, or Markdown formats.")

    def read_pdf(self, filename: str) -> str:
        """
        Reads text from a PDF file.

        Parameters:
        filename (str): The path to the PDF file.

        Returns:
        str: The text content of the PDF.

        Raises:
        FileNotFoundError: If the file does not exist.
        Exception: If any other error occurs during PDF reading.
        """
        if not os.path.exists(filename):
            raise FileNotFoundError("File not found")

        with open(filename, 'rb') as file:
            content = io.BytesIO(file.read())
            return self.extract_text_from_pdf(content)

    @staticmethod
    def read_txt(filename: str) -> str:
        """
        Reads text from a TXT file.

        Parameters:
        filename (str): The path to the TXT file.

        Returns:
        str: The text content of the TXT file.

        Raises:
        FileNotFoundError: If the file does not exist.
        Exception: If any other error occurs during text file reading.
        """
        if not os.path.exists(filename):
            raise FileNotFoundError("File not found")

        try:
            with open(filename, 'r', encoding='utf-8') as file:
                text = file.read()
            return text
        except Exception as e:
            raise Exception(f"Error reading TXT file: {str(e)}")

    def read_from_url(self, url: str) -> str:
        """
        Reads text from a URL.

        Parameters:
        url (str): The URL to read from.

        Returns:
        str: The text content of the URL.

        Raises:
        ValueError: If the file format is unsupported.
        requests.RequestException: If any HTTP error occurs.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            if url.endswith('.pdf'):
                return self.extract_text_from_pdf(io.BytesIO(response.content))
            elif url.endswith('.txt'):
                return response.text
            else:
                raise ValueError("Unsupported file format")
        except requests.RequestException as e:
            raise Exception(f"Error reading from URL: {str(e)}")

    @staticmethod
    def extract_text_from_pdf(file_stream: io.BytesIO) -> str:
        """
        Extracts text from a PDF file stream.

        Parameters:
        file_stream (io.BytesIO): The file stream of the PDF.

        Returns:
        str: The text content of the PDF.

        Raises:
        Exception: If any error occurs during PDF text extraction.
        """
        try:
            text = ""
            reader = pypdf.PdfReader(file_stream)
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")


if __name__ == "__main__":
    gettext_instance = GetText()
    filename_or_url = 'Documents'  # Replace with your file path or URL
    try:
        file_content = gettext_instance.read_file(filename_or_url)
        print(file_content)
    except Exception as exc:
        print(f"An error occurred: {str(exc)}")
