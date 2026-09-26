# Run baseline forums only
python main.py --phase 1a

# Run extension forums only
python main.py --phase 1b

# Run both forum phases
python main.py --phase 1

# Extract documentation
python main.py --phase 2

# Analyze source code
python main.py --phase 3

# Run everything
python main.py --phase all

# Filter results
python main.py --phase triage

# Generate summary
python main.py --phase summary