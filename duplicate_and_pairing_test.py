#!/usr/bin/env python3
"""
Backend Test Suite for Duplicate Ring Number Prevention and Pairing Functionality
Tests the two specific fixes mentioned in the review request:
1. Duplicate Ring Number Prevention
2. Breeding & Pairing Functionality
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL - use localhost for testing
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class DuplicateAndPairingTester:
    def __init__(self):
        self.test_results = []
        self.created_pigeons = []
        self.created_pairings = []
        
    def log_test(self, test_name, passed, message=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })
        
    def test_health_check(self):
        """Test if backend is running"""
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Health Check", True, f"Version: {data.get('version', 'unknown')}")
                return True
            else:
                self.log_test("Backend Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Connection error: {str(e)}")
            return False
            
    def clear_test_data(self):
        """Clear existing test data"""
        try:
            # Clear race results and races
            response = requests.delete(f"{API_BASE}/clear-test-data", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Clear Test Data", True, f"Cleared {data.get('races_deleted', 0)} races, {data.get('results_deleted', 0)} results")
                
                # Also clear any test pigeons we might have created
                pigeons_response = requests.get(f"{API_BASE}/pigeons", timeout=10)
                if pigeons_response.status_code == 200:
                    pigeons = pigeons_response.json()
                    for pigeon in pigeons:
                        if pigeon['ring_number'] in ['BE504727824', 'BE123456789', 'BE987654321', 'BE111222333', 'BE444555666']:
                            try:
                                requests.delete(f"{API_BASE}/pigeons/{pigeon['id']}", timeout=10)
                            except:
                                pass
                
                return True
            else:
                self.log_test("Clear Test Data", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Clear Test Data", False, f"Error: {str(e)}")
            return False
    
    def create_test_pigeon(self, ring_number, name, gender="male", birth_year=2022):
        """Create a test pigeon"""
        pigeon_data = {
            "ring_number": ring_number,
            "name": name,
            "gender": gender,
            "birth_year": birth_year,
            "color": "blue",
            "owner": "Test Owner"
        }
        
        try:
            response = requests.post(f"{API_BASE}/pigeons", json=pigeon_data, timeout=10)
            if response.status_code == 200:
                pigeon = response.json()
                self.created_pigeons.append(pigeon)
                return pigeon
            else:
                return None
        except Exception as e:
            return None
    
    # ========== DUPLICATE RING NUMBER PREVENTION TESTS ==========
    
    def test_duplicate_ring_number_prevention(self):
        """Test that creating a pigeon with an existing ring number is blocked"""
        print("\n" + "="*60)
        print("TESTING DUPLICATE RING NUMBER PREVENTION")
        print("="*60)
        
        # Test 1: Create initial pigeon with BE504727824
        ring_number = "BE504727824"
        pigeon_data = {
            "ring_number": ring_number,
            "name": "Original Pigeon",
            "gender": "male",
            "birth_year": 2022,
            "color": "blue",
            "owner": "Original Owner"
        }
        
        try:
            response = requests.post(f"{API_BASE}/pigeons", json=pigeon_data, timeout=10)
            if response.status_code == 200:
                original_pigeon = response.json()
                self.created_pigeons.append(original_pigeon)
                self.log_test("Create Original Pigeon", True, f"Created pigeon with ring {ring_number}")
            else:
                self.log_test("Create Original Pigeon", False, f"Failed to create original pigeon: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Create Original Pigeon", False, f"Error: {str(e)}")
            return False
        
        # Test 2: Try to create duplicate pigeon with same ring number
        duplicate_data = {
            "ring_number": ring_number,
            "name": "Duplicate Pigeon",
            "gender": "female",
            "birth_year": 2023,
            "color": "red",
            "owner": "Different Owner"
        }
        
        try:
            response = requests.post(f"{API_BASE}/pigeons", json=duplicate_data, timeout=10)
            if response.status_code == 400:
                error_data = response.json()
                expected_message = f"A pigeon with ring number {ring_number} already exists"
                if expected_message in error_data.get('detail', ''):
                    self.log_test("Duplicate Prevention - Correct Error", True, f"Got expected 400 error: {error_data['detail']}")
                else:
                    self.log_test("Duplicate Prevention - Correct Error", False, f"Wrong error message: {error_data.get('detail', 'No detail')}")
            else:
                self.log_test("Duplicate Prevention - Correct Error", False, f"Expected 400 error, got {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Duplicate Prevention - Correct Error", False, f"Error: {str(e)}")
            return False
        
        # Test 3: Verify original pigeon still exists unchanged
        try:
            response = requests.get(f"{API_BASE}/pigeons", timeout=10)
            if response.status_code == 200:
                pigeons = response.json()
                original_still_exists = any(p['ring_number'] == ring_number and p['name'] == 'Original Pigeon' for p in pigeons)
                duplicate_not_created = not any(p['ring_number'] == ring_number and p['name'] == 'Duplicate Pigeon' for p in pigeons)
                
                if original_still_exists and duplicate_not_created:
                    self.log_test("Original Pigeon Unchanged", True, "Original pigeon exists, duplicate was not created")
                else:
                    self.log_test("Original Pigeon Unchanged", False, "Original pigeon state changed or duplicate was created")
            else:
                self.log_test("Original Pigeon Unchanged", False, f"Failed to fetch pigeons: {response.status_code}")
        except Exception as e:
            self.log_test("Original Pigeon Unchanged", False, f"Error: {str(e)}")
        
        return True
    
    # ========== PAIRING FUNCTIONALITY TESTS ==========
    
    def test_pairing_functionality(self):
        """Test the new pairing endpoints"""
        print("\n" + "="*60)
        print("TESTING PAIRING FUNCTIONALITY")
        print("="*60)
        
        # Create test pigeons for pairing
        male_pigeon = self.create_test_pigeon("BE123456789", "Test Male", "male", 2021)
        female_pigeon = self.create_test_pigeon("BE987654321", "Test Female", "female", 2021)
        
        if not male_pigeon or not female_pigeon:
            self.log_test("Create Test Pigeons for Pairing", False, "Failed to create test pigeons")
            return False
        
        self.log_test("Create Test Pigeons for Pairing", True, f"Created male ({male_pigeon['ring_number']}) and female ({female_pigeon['ring_number']})")
        
        # Test 1: Create a new pairing
        pairing_data = {
            "sire_id": male_pigeon['id'],
            "dam_id": female_pigeon['id'],
            "expected_hatch_date": "2024-03-15",
            "notes": "Test pairing for breeding"
        }
        
        try:
            response = requests.post(f"{API_BASE}/pairings", json=pairing_data, timeout=10)
            if response.status_code == 200:
                pairing = response.json()
                self.created_pairings.append(pairing)
                self.log_test("Create Pairing", True, f"Created pairing with ID {pairing['id']}")
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                self.log_test("Create Pairing", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
                return False
        except Exception as e:
            self.log_test("Create Pairing", False, f"Error: {str(e)}")
            return False
        
        # Test 2: Get all pairings
        try:
            response = requests.get(f"{API_BASE}/pairings", timeout=10)
            if response.status_code == 200:
                pairings = response.json()
                found_pairing = any(p['id'] == pairing['id'] for p in pairings)
                self.log_test("Get Pairings", found_pairing, f"Found {len(pairings)} pairings, including our test pairing")
            else:
                self.log_test("Get Pairings", False, f"Failed to fetch pairings: {response.status_code}")
        except Exception as e:
            self.log_test("Get Pairings", False, f"Error: {str(e)}")
        
        # Test 3: Create offspring from pairing
        offspring_data = {
            "ring_number": "111222333",
            "country": "BE",
            "name": "Test Offspring",
            "gender": "male",
            "birth_year": 2024,
            "color": "checkered",
            "birth_date": "2024-03-20",
            "notes": "Offspring from test pairing"
        }
        
        try:
            response = requests.post(f"{API_BASE}/pairings/{pairing['id']}/result", json=offspring_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                offspring_pigeon = result.get('pigeon')
                pairing_result = result.get('pairing_result')
                
                if offspring_pigeon and pairing_result:
                    self.created_pigeons.append(offspring_pigeon)
                    expected_ring = "BE111222333"
                    if offspring_pigeon['ring_number'] == expected_ring:
                        self.log_test("Create Offspring", True, f"Created offspring with ring {expected_ring}")
                    else:
                        self.log_test("Create Offspring", False, f"Wrong ring number: expected {expected_ring}, got {offspring_pigeon['ring_number']}")
                else:
                    self.log_test("Create Offspring", False, "Missing pigeon or pairing_result in response")
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                self.log_test("Create Offspring", False, f"Status {response.status_code}: {error_data.get('detail', 'Unknown error')}")
        except Exception as e:
            self.log_test("Create Offspring", False, f"Error: {str(e)}")
        
        # Test 4: Verify offspring appears in pigeons collection
        try:
            response = requests.get(f"{API_BASE}/pigeons", timeout=10)
            if response.status_code == 200:
                pigeons = response.json()
                offspring_found = any(p['ring_number'] == 'BE111222333' for p in pigeons)
                if offspring_found:
                    offspring = next(p for p in pigeons if p['ring_number'] == 'BE111222333')
                    has_pedigree = offspring.get('sire_ring') == male_pigeon['ring_number'] and offspring.get('dam_ring') == female_pigeon['ring_number']
                    self.log_test("Offspring in Pigeons Collection", True, f"Offspring found with pedigree info: sire={offspring.get('sire_ring')}, dam={offspring.get('dam_ring')}")
                    
                    if not has_pedigree:
                        self.log_test("Pedigree Information", False, f"Missing pedigree: sire={offspring.get('sire_ring')}, dam={offspring.get('dam_ring')}")
                    else:
                        self.log_test("Pedigree Information", True, "Correct parent pedigree information stored")
                else:
                    self.log_test("Offspring in Pigeons Collection", False, "Offspring not found in pigeons collection")
            else:
                self.log_test("Offspring in Pigeons Collection", False, f"Failed to fetch pigeons: {response.status_code}")
        except Exception as e:
            self.log_test("Offspring in Pigeons Collection", False, f"Error: {str(e)}")
        
        return True
    
    def test_pairing_validation(self):
        """Test pairing validation (gender checks, duplicate ring numbers, etc.)"""
        print("\n" + "="*60)
        print("TESTING PAIRING VALIDATION")
        print("="*60)
        
        # Create additional test pigeons
        male_pigeon2 = self.create_test_pigeon("BE111222333", "Test Male 2", "male", 2022)
        female_pigeon2 = self.create_test_pigeon("BE444555666", "Test Female 2", "female", 2022)
        
        if not male_pigeon2 or not female_pigeon2:
            self.log_test("Create Additional Test Pigeons", False, "Failed to create additional test pigeons")
            return False
        
        # Test 1: Try to create pairing with non-existent pigeon
        invalid_pairing_data = {
            "sire_id": "non-existent-id",
            "dam_id": female_pigeon2['id'],
            "expected_hatch_date": "2024-04-15",
            "notes": "Invalid pairing test"
        }
        
        try:
            response = requests.post(f"{API_BASE}/pairings", json=invalid_pairing_data, timeout=10)
            if response.status_code == 404:
                error_data = response.json()
                self.log_test("Non-existent Pigeon Validation", True, f"Correctly rejected non-existent sire: {error_data.get('detail', '')}")
            else:
                self.log_test("Non-existent Pigeon Validation", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Non-existent Pigeon Validation", False, f"Error: {str(e)}")
        
        # Test 2: Try to create pairing with wrong genders (if gender validation is implemented)
        wrong_gender_pairing = {
            "sire_id": female_pigeon2['id'],  # Using female as sire
            "dam_id": male_pigeon2['id'],     # Using male as dam
            "expected_hatch_date": "2024-04-15",
            "notes": "Wrong gender test"
        }
        
        try:
            response = requests.post(f"{API_BASE}/pairings", json=wrong_gender_pairing, timeout=10)
            if response.status_code == 400:
                error_data = response.json()
                if "must be male" in error_data.get('detail', '') or "must be female" in error_data.get('detail', ''):
                    self.log_test("Gender Validation", True, f"Correctly rejected wrong genders: {error_data.get('detail', '')}")
                else:
                    self.log_test("Gender Validation", False, f"Wrong error message: {error_data.get('detail', '')}")
            else:
                self.log_test("Gender Validation", False, f"Expected 400 for gender validation, got {response.status_code}")
        except Exception as e:
            self.log_test("Gender Validation", False, f"Error: {str(e)}")
        
        # Test 3: Try to create offspring with duplicate ring number
        if self.created_pairings:
            pairing = self.created_pairings[0]
            duplicate_offspring_data = {
                "ring_number": "504727824",  # This should create BE504727824 which already exists
                "country": "BE",
                "name": "Duplicate Offspring",
                "gender": "female",
                "birth_year": 2024,
                "color": "white",
                "birth_date": "2024-04-01",
                "notes": "Duplicate ring test"
            }
            
            try:
                response = requests.post(f"{API_BASE}/pairings/{pairing['id']}/result", json=duplicate_offspring_data, timeout=10)
                if response.status_code == 400:
                    error_data = response.json()
                    if "already exists" in error_data.get('detail', ''):
                        self.log_test("Duplicate Ring in Offspring", True, f"Correctly prevented duplicate ring: {error_data.get('detail', '')}")
                    else:
                        self.log_test("Duplicate Ring in Offspring", False, f"Wrong error message: {error_data.get('detail', '')}")
                else:
                    self.log_test("Duplicate Ring in Offspring", False, f"Expected 400 for duplicate ring, got {response.status_code}")
            except Exception as e:
                self.log_test("Duplicate Ring in Offspring", False, f"Error: {str(e)}")
        
        return True
    
    def test_integration(self):
        """Test integration between pairing and pigeon systems"""
        print("\n" + "="*60)
        print("TESTING INTEGRATION")
        print("="*60)
        
        # Verify that all created pigeons exist
        try:
            response = requests.get(f"{API_BASE}/pigeons", timeout=10)
            if response.status_code == 200:
                pigeons = response.json()
                created_rings = {p['ring_number'] for p in self.created_pigeons}
                found_rings = {p['ring_number'] for p in pigeons if p['ring_number'] in created_rings}
                
                if created_rings == found_rings:
                    self.log_test("All Created Pigeons Exist", True, f"All {len(created_rings)} created pigeons found in database")
                else:
                    missing = created_rings - found_rings
                    self.log_test("All Created Pigeons Exist", False, f"Missing pigeons: {missing}")
            else:
                self.log_test("All Created Pigeons Exist", False, f"Failed to fetch pigeons: {response.status_code}")
        except Exception as e:
            self.log_test("All Created Pigeons Exist", False, f"Error: {str(e)}")
        
        # Verify pairings exist
        try:
            response = requests.get(f"{API_BASE}/pairings", timeout=10)
            if response.status_code == 200:
                pairings = response.json()
                created_pairing_ids = {p['id'] for p in self.created_pairings}
                found_pairing_ids = {p['id'] for p in pairings if p['id'] in created_pairing_ids}
                
                if created_pairing_ids == found_pairing_ids:
                    self.log_test("All Created Pairings Exist", True, f"All {len(created_pairing_ids)} created pairings found in database")
                else:
                    missing = created_pairing_ids - found_pairing_ids
                    self.log_test("All Created Pairings Exist", False, f"Missing pairings: {missing}")
            else:
                self.log_test("All Created Pairings Exist", False, f"Failed to fetch pairings: {response.status_code}")
        except Exception as e:
            self.log_test("All Created Pairings Exist", False, f"Error: {str(e)}")
        
        return True
    
    def run_comprehensive_test(self):
        """Run the comprehensive test suite for duplicate prevention and pairing functionality"""
        print("=" * 80)
        print("BACKEND TEST SUITE - DUPLICATE PREVENTION & PAIRING FUNCTIONALITY")
        print("=" * 80)
        print(f"Backend URL: {BACKEND_URL}")
        print("Testing two specific fixes:")
        print("1. Duplicate Ring Number Prevention")
        print("2. Breeding & Pairing Functionality")
        print()
        
        # Test 1: Health check
        if not self.test_health_check():
            print("❌ Backend not available - stopping tests")
            return False
            
        # Test 2: Clear existing data
        self.clear_test_data()
        
        # Test 3: Duplicate ring number prevention
        self.test_duplicate_ring_number_prevention()
        
        # Test 4: Pairing functionality
        self.test_pairing_functionality()
        
        # Test 5: Pairing validation
        self.test_pairing_validation()
        
        # Test 6: Integration tests
        self.test_integration()
        
        # Summary
        print()
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for t in self.test_results if t['passed'])
        total = len(self.test_results)
        
        print(f"Tests passed: {passed}/{total}")
        
        # Group results by category
        duplicate_tests = [t for t in self.test_results if 'Duplicate' in t['test'] or 'Original Pigeon' in t['test']]
        pairing_tests = [t for t in self.test_results if 'Pairing' in t['test'] or 'Offspring' in t['test'] or 'Pedigree' in t['test']]
        validation_tests = [t for t in self.test_results if 'Validation' in t['test'] or 'Gender' in t['test']]
        
        print(f"\nDuplicate Prevention Tests: {sum(1 for t in duplicate_tests if t['passed'])}/{len(duplicate_tests)}")
        print(f"Pairing Functionality Tests: {sum(1 for t in pairing_tests if t['passed'])}/{len(pairing_tests)}")
        print(f"Validation Tests: {sum(1 for t in validation_tests if t['passed'])}/{len(validation_tests)}")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Duplicate ring number prevention is working correctly")
            print("✅ Pairing functionality is working end-to-end")
            print("✅ All validation is working correctly")
            return True
        else:
            print("\n❌ Some tests failed:")
            for test in self.test_results:
                if not test['passed']:
                    print(f"   FAILED: {test['test']} - {test['message']}")
            return False

if __name__ == "__main__":
    tester = DuplicateAndPairingTester()
    success = tester.run_comprehensive_test()
    exit(0 if success else 1)