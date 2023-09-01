# Meetoptics-exercises
Meetoptics exercises
Optics Product Data Extraction and Integration

This repository contains Python scripts and tools for extracting product information from two optics suppliers, OptoSigma and Thorlabs, and then unifying and homogenizing the specifications for integration into a single database.

Task 1: Extracting OptoSigma Optics Products

Utilizes Python to perform a web request to the OptoSigma website (https://www.optosigma.com/eu_en/fused-silica-plano-convex-lenses-uncoated-SLSQ-P.html).
Processes the HTML using Beautiful Soup to generate a dictionary with product codes as keys and specification-value pairs as children.
Saves the resulting dictionary to a JSON file.

Task 2: Extracting Thorlabs Optics Products
Replicates the data extraction process for Thorlabs optics using the link (https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=3279).

Task 3: Comparing and Homogenizing Specifications
Identifies a set of 6 relevant lens specifications.
Implements a script to identify these specifications in both OptoSigma and Thorlabs product data, using regex pattern matching for text cleaning and standardization.
Generates new JSON files with the homogenized specification names for seamless integration.
By centralizing and standardizing optics product data from these two suppliers, this repository facilitates easy comparison and integration of lens specifications, making it a valuable resource for optical engineers and researchers.
