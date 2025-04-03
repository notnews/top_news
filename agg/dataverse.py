#!/usr/bin/env python3
"""
Dataverse File Uploader
A script to upload files to Harvard Dataverse or other Dataverse instances.
"""

import os
import argparse
import requests
import sys
from tqdm import tqdm
import mimetypes

class DataverseUploader:
    def __init__(self, server_url, api_token, dataset_id):
        """Initialize the uploader with server info and credentials."""
        self.server_url = server_url.rstrip('/')
        self.api_token = api_token
        self.dataset_id = dataset_id
        self.upload_url = f"{self.server_url}/api/datasets/:persistentId/add"

    def _get_mimetype(self, file_path):
        """Determine the MIME type based on file extension."""
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Default mappings for common compressed file types
        if file_path.endswith('.tar.gz') or file_path.endswith('.tgz'):
            return 'application/x-gzip'
        elif file_path.endswith('.gz'):
            return 'application/gzip'
        elif file_path.endswith('.zip'):
            return 'application/zip'
        elif file_path.endswith('.csv'):
            return 'text/csv'
        elif file_path.endswith('.json'):
            return 'application/json'
        
        # Use detected MIME type or default to octet-stream
        return mime_type or 'application/octet-stream'

    def upload_file(self, file_path, description=None):
        """Upload a file to the Dataverse dataset."""
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return False

        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)
        mime_type = self._get_mimetype(file_path)
        
        print(f"Uploading {filename} ({self._format_size(file_size)}) to dataset {self.dataset_id}...")
        
        # Set up parameters for the request
        params = {
            'persistentId': self.dataset_id,
            'key': self.api_token
        }
        
        # Add description if provided
        if description:
            params['description'] = description

        try:
            with open(file_path, 'rb') as file_obj:
                files = {
                    'file': (filename, file_obj, mime_type)
                }
                
                # Use tqdm to show progress (note: actual progress tracking is limited)
                with tqdm(total=100, unit="%") as pbar:
                    # We can't track actual upload progress with simple requests
                    # So we'll update at key points
                    pbar.update(10)  # Starting upload
                    
                    response = requests.post(
                        self.upload_url, 
                        params=params,
                        files=files
                    )
                    
                    pbar.update(90)  # Completed upload
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                file_id = result['data']['files'][0]['dataFile']['id']
                persistent_id = result.get('data', {}).get('files', [{}])[0].get('dataFile', {}).get('persistentId', 'Not available')
                
                print(f"✅ Upload successful!")
                print(f"File ID: {file_id}")
                if persistent_id != 'Not available':
                    print(f"Persistent ID: {persistent_id}")
                return True
            else:
                print(f"❌ Upload failed with status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error during upload: {str(e)}")
            return False

    def _format_size(self, size_bytes):
        """Format file size in a human-readable format."""
        if size_bytes == 0:
            return "0B"
        size_names = ("B", "KB", "MB", "GB", "TB")
        i = int(min(4, int(min(4, max(0, int(size_bytes > 0) - 1)) + min(4, max(0, int(size_bytes > 0) - 1)) * int(size_bytes > 0) + int(min(4, max(0, int(size_bytes > 0) - 1)) + min(4, max(0, int(size_bytes > 0) - 1)) * int(size_bytes > 0) < int(math.log(size_bytes, 1024)))) if size_bytes > 0 else 0)
        p = 1024.0 ** i
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Upload files to a Dataverse instance.')
    parser.add_argument('file_path', help='Path to the file to upload')
    parser.add_argument('--server', default='https://dataverse.harvard.edu', 
                        help='Dataverse server URL (default: https://dataverse.harvard.edu)')
    parser.add_argument('--token', required=True, help='API token for authentication')
    parser.add_argument('--dataset', required=True, help='Dataset persistent ID (e.g., doi:10.7910/DVN/XXXXXXX)')
    parser.add_argument('--description', help='Optional description for the file')
    
    args = parser.parse_args()
    
    # Create uploader and perform upload
    uploader = DataverseUploader(args.server, args.token, args.dataset)
    success = uploader.upload_file(args.file_path, args.description)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    # Import math here to fix the _format_size function which uses math.log
    import math
    main()