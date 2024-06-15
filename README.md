# SUNRISE_gChinarro
Repositorio para el trabajo de SUNRISE realizado por Guillermo Chinarro

# Blockchain-based Physical Unclonable Functions Authentication System

## Overview
This project demonstrates a blockchain-based Physical Unclonable Functions authentication system. It utilizes Physical Unclonable Functions (PUFs) for generating challenges and responses and a Blockchain for validating the challenge-response pairs.

## Components
1. **Main Script (`main.py`)**:
   - The main entry point of the application.
   - Initializes parameters such as the PUF name and number of blocks.
   - Validates challenges with the blockchain.

2. **Blockchain Validation (`blockchain_validation.py`)**:
   - Contains classes for Block and Blockchain.
   - Implements methods for creating blocks, adding blocks to the blockchain, and validating the blockchain.
   - Validates challenge-response pairs against the PUF.

3. **PUF Challenge Response (`puf_challenge_response.py`)**:
   - Implements functions for generating PUF challenge-response pairs.
   - Utilizes PUF simulation from `pypuf` library.
   - Generates challenges and evaluates responses using the PUF.

4. **PUF BER Entropy Script (`puf_ber_entropy.py`)**:
   - Calculates the bit error rate (BER) and entropy of PUF responses.
   - Helps evaluate the quality and security of the responses generated by PUFs.

5. **PUF Reproducibility and Uniqueness Script (`puf_reproducibility_uniqueness.py`)**:
   - Evaluates the reproducibility and uniqueness of PUF responses
   - Provides metrics to ensure that PUF responses are consistent and unique between different devices.

## Usage
1. **Setup**:
   - Ensure Python 3.11 is installed on your system.
   - Install required dependencies using `pip install -r requirements.txt`.

2. **Run the Application**:
   - Execute the `main.py` script to run the application.
   - Adjust parameters in `main.py` as needed for your use case.
   - Another alternative is to run the scripts `puf_ber_entropy.py` or `puf_reproducibility_uniqueness.py` separately to obtain their metrics.

## PUFs Supported
- ArbiterPUF
- XORArbiterPUF
- XORFeedForwardArbiterPUF
- BistableRingPUF
- XORBistableRingPUF
- InterposePUF
- LightweightSecurePUF
- PermutationPUF

## Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, please submit an issue or a pull request.

## License
This project is licensed under the GNU License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- This project utilizes the `pypuf` library for PUF simulation.
- Special thanks to the developers of the blockchain and cryptography libraries used in this project.
- DOI [10.5281/zenodo.3901410](https://doi.org/10.5281/zenodo.3901410)
