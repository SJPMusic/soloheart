#!/usr/bin/env python3
"""
Web UI verification script.

Checks if the web server is running and verifies that all API endpoints
are responding correctly. Useful for quick verification during development.
"""

import requests
import json
import time
import sys
from datetime import datetime

class WebUIVerifier:
    """Verifies web UI functionality."""
    
    def __init__(self, base_url="http://localhost:5001", campaign_id="test-campaign"):
        self.base_url = base_url
        self.campaign_id = campaign_id
        self.session = requests.Session()
        self.results = {}
    
    def check_server_running(self):
        """Check if the web server is running."""
        print("🔄 Checking if web server is running...")
        
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ Web server is running")
                return {"success": True, "status_code": response.status_code}
            else:
                print(f"❌ Web server returned status {response.status_code}")
                return {"success": False, "status_code": response.status_code}
        except requests.exceptions.ConnectionError:
            print("❌ Web server is not running")
            return {"success": False, "error": "Connection refused"}
        except Exception as e:
            print(f"❌ Error checking server: {e}")
            return {"success": False, "error": str(e)}
    
    def test_api_endpoint(self, endpoint, method="GET", data=None, description=None):
        """Test a specific API endpoint."""
        if description is None:
            description = f"{method} {endpoint}"
        
        print(f"🔄 Testing {description}...")
        
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {"Content-Type": "application/json"} if data else {}
            
            if method == "GET":
                response = self.session.get(url, timeout=10)
            elif method == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=10)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    print(f"✅ {description} - PASSED")
                    return {"success": True, "status_code": response.status_code, "data": json_data}
                except json.JSONDecodeError:
                    print(f"⚠️ {description} - RESPONDED BUT NOT JSON")
                    return {"success": True, "status_code": response.status_code, "data": response.text}
            else:
                print(f"❌ {description} - FAILED (Status: {response.status_code})")
                return {"success": False, "status_code": response.status_code, "error": response.text}
                
        except requests.exceptions.Timeout:
            print(f"❌ {description} - TIMEOUT")
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            print(f"❌ {description} - ERROR: {e}")
            return {"success": False, "error": str(e)}
    
    def verify_lore_endpoints(self):
        """Verify lore-related endpoints."""
        print("\n📚 Verifying Lore Endpoints...")
        
        results = {}
        
        # Test GET lore endpoint
        results["get_lore"] = self.test_api_endpoint(
            f"/api/campaign/{self.campaign_id}/lore",
            description="GET lore entries"
        )
        
        # Test POST lore endpoint
        test_lore = {
            "title": "Test Lore Entry",
            "content": "This is a test lore entry for verification.",
            "lore_type": "test",
            "importance": 1,
            "tags": ["test", "verification"],
            "discovered": True
        }
        
        results["post_lore"] = self.test_api_endpoint(
            f"/api/campaign/{self.campaign_id}/lore",
            method="POST",
            data=test_lore,
            description="POST new lore entry"
        )
        
        return results
    
    def verify_diagnostics_endpoints(self):
        """Verify diagnostics-related endpoints."""
        print("\n📊 Verifying Diagnostics Endpoints...")
        
        results = {}
        
        # Test diagnostics endpoints
        endpoints = [
            ("/diagnostics/timeline", "GET diagnostics timeline"),
            ("/diagnostics/arcs", "GET diagnostics arcs"),
            ("/diagnostics/heatmap", "GET diagnostics heatmap"),
            ("/diagnostics/report", "GET diagnostics report")
        ]
        
        for endpoint, description in endpoints:
            results[endpoint.replace("/", "_")] = self.test_api_endpoint(
                f"/api/campaign/{self.campaign_id}{endpoint}",
                description=description
            )
        
        return results
    
    def verify_campaign_endpoints(self):
        """Verify campaign-related endpoints."""
        print("\n🎮 Verifying Campaign Endpoints...")
        
        results = {}
        
        # Test campaign endpoints
        endpoints = [
            ("/summary", "GET campaign summary"),
            ("/sidebar", "GET sidebar data"),
            ("/chat/history", "GET chat history"),
            ("/orchestration/events", "GET orchestration events"),
            ("/narrative-dynamics", "GET narrative dynamics"),
            ("/conflicts", "GET conflicts")
        ]
        
        for endpoint, description in endpoints:
            results[endpoint.replace("/", "_")] = self.test_api_endpoint(
                f"/api/campaign/{self.campaign_id}{endpoint}",
                description=description
            )
        
        return results
    
    def verify_action_endpoint(self):
        """Verify action processing endpoint."""
        print("\n⚔️ Verifying Action Endpoint...")
        
        test_action = {
            "action": "I test the verification system",
            "character_id": "player",
            "context": "Testing"
        }
        
        return {
            "post_action": self.test_api_endpoint(
                f"/api/campaign/{self.campaign_id}/action",
                method="POST",
                data=test_action,
                description="POST player action"
            )
        }
    
    def verify_character_endpoints(self):
        """Verify character management endpoints."""
        print("\n👤 Verifying Character Endpoints...")
        
        results = {}
        
        # Test character endpoints
        results["get_characters"] = self.test_api_endpoint(
            f"/api/campaign/{self.campaign_id}/characters",
            description="GET characters"
        )
        
        # Test character activation
        results["activate_character"] = self.test_api_endpoint(
            f"/api/campaign/{self.campaign_id}/characters/player/activate",
            method="POST",
            description="POST activate character"
        )
        
        return results
    
    def run_verification(self):
        """Run complete verification."""
        print("🔍 Web UI Verification")
        print("=" * 50)
        print(f"🌐 Base URL: {self.base_url}")
        print(f"🆔 Campaign ID: {self.campaign_id}")
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check server status
        server_status = self.check_server_running()
        if not server_status["success"]:
            print("\n❌ Cannot proceed - web server is not running")
            print("💡 Start the server with: python web_interface.py")
            return {"success": False, "error": "Server not running"}
        
        # Run all verifications
        self.results["server_status"] = server_status
        self.results["lore_endpoints"] = self.verify_lore_endpoints()
        self.results["diagnostics_endpoints"] = self.verify_diagnostics_endpoints()
        self.results["campaign_endpoints"] = self.verify_campaign_endpoints()
        self.results["action_endpoint"] = self.verify_action_endpoint()
        self.results["character_endpoints"] = self.verify_character_endpoints()
        
        # Generate summary
        self.print_summary()
        
        return self.results
    
    def print_summary(self):
        """Print verification summary."""
        print("\n" + "=" * 50)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 50)
        
        total_tests = 0
        passed_tests = 0
        
        for category, results in self.results.items():
            if category == "server_status":
                if results["success"]:
                    passed_tests += 1
                total_tests += 1
                continue
                
            for test_name, result in results.items():
                total_tests += 1
                if result["success"]:
                    passed_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 Category Results:")
        for category, results in self.results.items():
            if category == "server_status":
                status = "✅ PASS" if results["success"] else "❌ FAIL"
                print(f"  {status} Server Status")
                continue
                
            category_passed = sum(1 for result in results.values() if result["success"])
            category_total = len(results)
            category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
            
            status = "✅" if category_passed == category_total else "⚠️" if category_passed > 0 else "❌"
            print(f"  {status} {category.replace('_', ' ').title()}: {category_passed}/{category_total} ({category_rate:.0f}%)")
        
        if passed_tests == total_tests:
            print(f"\n🎉 All verifications passed! Web UI is fully operational.")
        elif passed_tests > total_tests * 0.8:
            print(f"\n⚠️ Most verifications passed. Check failed endpoints above.")
        else:
            print(f"\n❌ Many verifications failed. Please check server configuration.")
        
        print(f"\n🌐 Access the web UI at: {self.base_url}")
    
    def save_report(self, filename=None):
        """Save verification report to file."""
        if filename is None:
            filename = f"web_ui_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "verification": {
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "campaign_id": self.campaign_id
            },
            "results": self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Verification report saved to: {filename}")
        return filename


def main():
    """Main function to run verification."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify Web UI functionality")
    parser.add_argument("--url", default="http://localhost:5001", help="Base URL of web server")
    parser.add_argument("--campaign", default="test-campaign", help="Campaign ID to test")
    parser.add_argument("--save-report", help="Save report to specified file")
    
    args = parser.parse_args()
    
    verifier = WebUIVerifier(args.url, args.campaign)
    
    try:
        results = verifier.run_verification()
        
        if args.save_report:
            verifier.save_report(args.save_report)
        else:
            verifier.save_report()
        
        # Exit with appropriate code
        total_tests = sum(len(results[cat]) if cat != "server_status" else 1 for cat in results)
        passed_tests = sum(
            sum(1 for result in results[cat].values() if result["success"])
            if cat != "server_status" else (1 if results[cat]["success"] else 0)
            for cat in results
        )
        
        if passed_tests == total_tests:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 