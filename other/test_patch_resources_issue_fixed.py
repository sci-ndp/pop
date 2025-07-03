# test_patch_resources_issue_fixed.py
# Script to replicate the PATCH resources issue #92 with organization creation

import requests
import json

# Configuration - adjust these values for your environment
BASE_URL = "http://localhost:8003"  # Your API base URL
USERNAME = "testing_name"  # Your test username
PASSWORD = "testing_password"  # Your test password
ORG_NAME = "test_org"  # Organization name to create

def get_auth_token():
    """Get authentication token from the API."""
    try:
        response = requests.post(
            f"{BASE_URL}/token",
            data={
                "username": USERNAME,
                "password": PASSWORD
            }
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"Error getting auth token: {e}")
        return None

def create_test_organization(token):
    """Create test organization if it doesn't exist."""
    headers = {"Authorization": f"Bearer {token}"}
    
    org_data = {
        "name": ORG_NAME,
        "title": "Test Organization",
        "description": "Organization created for testing PATCH resources functionality"
    }
    
    try:
        # Try to create in local server (default)
        response = requests.post(
            f"{BASE_URL}/organization?server=local",
            json=org_data,
            headers=headers
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Created organization: {result['id']}")
            return True
        elif response.status_code == 400:
            response_text = response.text.lower()
            if "already exists" in response_text or "name already" in response_text:
                print(f"✅ Organization '{ORG_NAME}' already exists")
                return True
            else:
                print(f"❌ Error creating organization: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        else:
            print(f"❌ Error creating organization: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating organization: {e}")
        return False

def alternative_org_check(token):
    """Alternative method to check if we can use the organization."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to create a minimal test dataset to see if the org works
    test_data = {
        "name": "temp_test_dataset_check_org",
        "title": "Temporary Test Dataset",
        "owner_org": ORG_NAME,
        "notes": "Temporary dataset to verify organization exists"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/dataset",
            json=test_data,
            headers=headers
        )
        
        if response.status_code == 201:
            # Organization works! Clean up the test dataset
            result = response.json()
            dataset_id = result.get('id')
            if dataset_id:
                # Delete the test dataset
                try:
                    requests.delete(
                        f"{BASE_URL}/resource",
                        params={"resource_id": dataset_id},
                        headers=headers
                    )
                except:
                    pass  # Ignore cleanup errors
            
            print(f"✅ Organization '{ORG_NAME}' is working (verified by test dataset)")
            return True
        else:
            error_text = response.text.lower()
            if "organization does not exist" in error_text:
                print(f"❌ Organization '{ORG_NAME}' does not exist in local CKAN")
                return False
            else:
                print(f"⚠️  Organization check inconclusive: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error in alternative organization check: {e}")
        return False

def check_organization_exists(token):
    """Check if the organization exists in the local server."""
    try:
        # Check local organizations using server=local parameter
        response = requests.get(f"{BASE_URL}/organization?server=local")
        response.raise_for_status()
        organizations = response.json()
        
        if ORG_NAME in organizations:
            print(f"✅ Organization '{ORG_NAME}' exists in local server")
            return True
        else:
            print(f"❌ Organization '{ORG_NAME}' not found in local server")
            print(f"Available local organizations: {organizations}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking organizations: {e}")
        return False

def create_test_dataset(token):
    """Create a test dataset to work with."""
    headers = {"Authorization": f"Bearer {token}"}
    
    dataset_data = {
        "name": "test_patch_resources_dataset",
        "title": "Test Dataset for PATCH Resources",
        "owner_org": ORG_NAME,
        "notes": "Dataset to test PATCH resources functionality",
        "resources": [
            {
                "url": "http://example.com/initial.csv",
                "name": "initial_resource",
                "format": "CSV",
                "description": "Initial resource"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/dataset",
            json=dataset_data,
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        print(f"✅ Created test dataset: {result['id']}")
        return result["id"]
    except Exception as e:
        print(f"❌ Error creating dataset: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return None

def get_dataset_details(dataset_id, token):
    """Get current dataset details including resources."""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Using search to get dataset details
        response = requests.post(
            f"{BASE_URL}/search",
            json={"dataset_name": "test_patch_resources_dataset", "server": "local"},
            headers=headers
        )
        response.raise_for_status()
        results = response.json()
        
        if results:
            dataset = results[0]
            print(f"📋 Dataset: {dataset['name']}")
            print(f"📋 Resources count: {len(dataset.get('resources', []))}")
            for i, resource in enumerate(dataset.get('resources', [])):
                print(f"   Resource {i+1}: {resource['name']} - {resource['url']}")
            return dataset
        else:
            print("❌ Dataset not found in search results")
            return None
    except Exception as e:
        print(f"❌ Error getting dataset details: {e}")
        return None

def patch_add_resource(dataset_id, token):
    """Try to add a resource using PATCH endpoint."""
    headers = {"Authorization": f"Bearer {token}"}
    
    patch_data = {
        "resources": [
            {
                "url": "http://example.com/patch-added.json",
                "name": "patch_added_resource",
                "format": "JSON",
                "description": "Resource added via PATCH"
            }
        ]
    }
    
    try:
        response = requests.patch(
            f"{BASE_URL}/dataset/{dataset_id}",
            json=patch_data,
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        print(f"✅ PATCH request successful: {result}")
        return True
    except Exception as e:
        print(f"❌ Error patching dataset: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return False

def cleanup_test_data(dataset_id, token):
    """Clean up test data created during the test."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🧹 Cleaning up test data...")
    
    # Delete dataset
    if dataset_id:
        try:
            response = requests.delete(
                f"{BASE_URL}/resource",
                params={"resource_id": dataset_id},
                headers=headers
            )
            if response.status_code == 200:
                print("✅ Test dataset deleted")
            else:
                print(f"⚠️  Could not delete dataset: {response.status_code}")
        except Exception as e:
            print(f"⚠️  Error deleting dataset: {e}")
    
    # Note: We don't delete the organization as it might be used by other tests

def main():
    """Main function to replicate the issue."""
    print("🔍 Testing PATCH resources issue #92")
    print("=" * 50)
    
    # Step 1: Get authentication token
    print("1. Getting authentication token...")
    token = get_auth_token()
    if not token:
        print("❌ Failed to get auth token. Exiting.")
        return
    
    # Step 2: Ensure organization exists
    print("\n2. Ensuring test organization exists...")
    org_created = create_test_organization(token)
    if not org_created:
        print("❌ Failed to create/verify organization. Exiting.")
        return
    
    # Step 3: Double-check organization exists
    print("\n3. Verifying organization exists...")
    org_exists = check_organization_exists(token)
    if not org_exists:
        print("⚠️  Standard organization check failed. Trying alternative method...")
        org_exists = alternative_org_check(token)
        if not org_exists:
            print("❌ Organization verification failed completely. Exiting.")
            return
    
    # Step 4: Create test dataset with initial resource
    print("\n4. Creating test dataset...")
    dataset_id = create_test_dataset(token)
    if not dataset_id:
        print("❌ Failed to create dataset. Exiting.")
        return
    
    # Step 5: Get initial dataset state
    print("\n5. Getting initial dataset state...")
    initial_state = get_dataset_details(dataset_id, token)
    if not initial_state:
        print("❌ Failed to get initial state. Exiting.")
        cleanup_test_data(dataset_id, token)
        return
    
    initial_resource_count = len(initial_state.get('resources', []))
    print(f"📊 Initial resource count: {initial_resource_count}")
    
    # Step 6: Try to add resource via PATCH
    print("\n6. Adding resource via PATCH...")
    patch_success = patch_add_resource(dataset_id, token)
    if not patch_success:
        print("❌ PATCH request failed. Exiting.")
        cleanup_test_data(dataset_id, token)
        return
    
    # Step 7: Check if resource was actually added
    print("\n7. Checking if resource was added...")
    final_state = get_dataset_details(dataset_id, token)
    if not final_state:
        print("❌ Failed to get final state.")
        cleanup_test_data(dataset_id, token)
        return
    
    final_resource_count = len(final_state.get('resources', []))
    print(f"📊 Final resource count: {final_resource_count}")
    
    # Step 8: Verify the issue
    print("\n8. Issue verification:")
    if final_resource_count > initial_resource_count:
        print("✅ SUCCESS: Resource was added correctly")
        print("   The issue might be resolved or not reproducible in this environment")
        issue_confirmed = False
    else:
        print("❌ ISSUE CONFIRMED: Resource was NOT added")
        print("   PATCH reported success but resource count didn't increase")
        print("   This confirms issue #92")
        issue_confirmed = True
    
    # Step 9: Detailed analysis
    print("\n9. Detailed analysis:")
    print(f"   Initial resources: {[r['name'] for r in initial_state.get('resources', [])]}")
    print(f"   Final resources: {[r['name'] for r in final_state.get('resources', [])]}")
    
    if issue_confirmed:
        print("\n❌ ISSUE ANALYSIS:")
        print("   - PATCH endpoint reported success")
        print("   - But resources were replaced instead of added")
        print("   - Expected behavior: ADD new resources to existing ones")
        print("   - Actual behavior: REPLACE all resources with new ones")
    else:
        print("\n✅ ISSUE STATUS:")
        print("   - PATCH endpoint worked correctly")
        print("   - Resources were added as expected")
        print("   - Issue #92 appears to be resolved")
    
    # Step 10: Cleanup
    cleanup_test_data(dataset_id, token)
    
    print("\n" + "=" * 50)
    print("🔍 Test completed")
    
    # Return status for automation
    return not issue_confirmed

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)  # Exit with error code if issue is confirmed