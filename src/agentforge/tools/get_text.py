# get_text.py
import requests
import io
from pathlib import Path
import pypdf


class GetText:
    @staticmethod
    def resolve_path(filename: str) -> Path:
        """
        Resolves a given path to an absolute path and validates its existence.

        Parameters:
        filename (str): The file path to resolve.

        Returns:
        Path: A resolved absolute path.

        Raises:
        FileNotFoundError: If the file does not exist.
        """
        path = Path(filename).expanduser().resolve()

        if not path.is_file():
            raise FileNotFoundError(f"{path}")

        return path

    def read_file(self, file_name_or_url: str) -> str:
        """
        Reads text content from a file or URL.

        Parameters:
        file_name_or_url (str): The path to the file or the URL to read.

        Returns:
        str: The text content of the file or URL.

        Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is unsupported.
        Exception: For general errors during reading.
        """
        if file_name_or_url.startswith(('http://', 'https://')):
            return self.read_from_url(file_name_or_url)

        if file_name_or_url.endswith('.pdf'):
            return self.read_pdf(file_name_or_url)

        if file_name_or_url.endswith(('.txt', '.md')):
            return self.read_txt(file_name_or_url)

        raise ValueError("Unsupported file format - Use a URL or File with PDF, TXT, or Markdown formats.")

    def read_pdf(self, filename: str) -> str:
        """
        Reads text content from a PDF file.

        Parameters:
        filename (str): The path to the PDF file.

        Returns:
        str: The text content of the PDF.

        Raises:
        FileNotFoundError: If the file does not exist.
        Exception: For errors during PDF text extraction.
        """
        path = self.resolve_path(filename)

        try:
            with path.open('rb') as file:
                content = io.BytesIO(file.read())
                return self.extract_text_from_pdf(content)
        except Exception as e:
            raise Exception(f"Error reading PDF file: {str(e)}")

    def read_txt(self, filename: str) -> str:
        """
        Reads text content from a TXT file.

        Parameters:
        filename (str): The path to the TXT file.

        Returns:
        str: The text content of the TXT file.

        Raises:
        FileNotFoundError: If the file does not exist.
        Exception: For errors during TXT file reading.
        """
        path = self.resolve_path(filename)

        try:
            return path.read_text(encoding='utf-8')
        except Exception as e:
            raise Exception(f"Error reading TXT file: {str(e)}")

    def read_from_url(self, url: str) -> str:
        """
        Reads text content from a URL.

        Parameters:
        url (str): The URL to read from.

        Returns:
        str: The text content of the URL.

        Raises:
        ValueError: If the file format is unsupported.
        requests.RequestException: For HTTP errors during URL reading.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()

            if url.endswith('.pdf'):
                return self.extract_text_from_pdf(io.BytesIO(response.content))

            if url.endswith('.txt') or url.endswith('.md'):
                return response.text

            raise ValueError("Unsupported file format for URL - Use PDF, TXT or Markdown formats.")
        except requests.RequestException as e:
            raise Exception(f"Error reading from URL: {str(e)}")

    @staticmethod
    def extract_text_from_pdf(file_stream: io.BytesIO) -> str:
        """
        Extracts text content from a PDF file stream.

        Parameters:
        file_stream (io.BytesIO): The file stream of the PDF.

        Returns:
        str: The extracted text content of the PDF.

        Raises:
        Exception: For errors during PDF text extraction.
        """
        try:
            text = ""
            reader = pypdf.PdfReader(file_stream)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")


if __name__ == "__main__":
    gettext_instance = GetText()
    filename_or_url = 'Documents/sample.pdf'  # Replace with your file path or URL
    try:
        file_content = gettext_instance.read_file(filename_or_url)
        print(file_content)
    except Exception as exc:
        print(f"An error occurred: {str(exc)}")
