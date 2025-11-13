import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# The class name is "Mortgage Payment Calculator" 
class MortgagePaymentCalculator:
    """
    Calculates various mortgage payment types and generates a loan amortization 
    and payment schedule using NumPy, Pandas, and Matplotlib.
    """
    
    def __init__(self, principal, interestrate, amortization_period, term):
        """
        Initializes the calculator with loan parameters.
        Amortization Period (in years) is for calculating the payment amount.
        Term (in years) is for generating the payment schedule.
        """
        self.principal = principal
        self.interestrate = interestrate / 100  # Converts Percentage to Decimal
        self.amortization_period = amortization_period
        self.term = term
        
        # --- Convert Yearly Interest Rate to Various Periodic Rates ---
        
        # Calculate Monthly Interest Rate
        # Formula: (1 + Yearly Rate/2)^(2/12) - 1
        self.monthlyinterestrate = (1 + self.interestrate / 2)**(2 / 12) - 1 

        # Calculate Semi-Monthly Interest Rate
        # Formula: (1 + Yearly Rate/2)^(2/24) - 1
        self.semimonthlyinterestrate = (1 + self.interestrate / 2)**(2 / 24) - 1 

        # Calculate Bi-Weekly Interest Rate (Actual Bi-weekly, 26 payments/year)
        # Formula: (1 + Yearly Rate/2)^(2/26) - 1
        self.biweeklyinterestrate = (1 + self.interestrate / 2)**(2 / 26) - 1 
        
        # Calculate Weekly Interest Rate
        # Formula: (1 + Yearly Rate/2)^(2/52) - 1
        self.weeklyinterestrate = (1 + self.interestrate / 2)**(2 / 52) - 1 

    def calculatepayments(self):
        """
        Calculates the payment amounts for all six options.
        Returns a tuple of the six payment amounts.
        """
        
        # Total number of compounding periods for Amortization (n)
        # Assuming semi-annual compounding for payment calculation as per Canadian standard
        n_months = self.amortization_period * 12

        # Defined the PVM formula as an internal function 
        # P = Principal * (r * (1 + r)^n) / ((1 + r)^n - 1)
        def calculate_payment(periodic_rate, periods):
            if periodic_rate == 0:
                return self.principal / periods
            return (self.principal * (periodic_rate * (1 + periodic_rate)**periods)) / \
                   ((1 + periodic_rate)**periods - 1)

        # 1. Monthly Payment (12 times a year)
        MonthlyPayment = calculate_payment(self.monthlyinterestrate, n_months)
        
        # 2. Semi-Monthly Payment (24 times a year)
        SemiMonthlyPayment = calculate_payment(self.semimonthlyinterestrate, n_months * 2)

        # 3. Bi-Weekly Payment (26 times a year)
        BiweeklyPayment = calculate_payment(self.biweeklyinterestrate, n_months * (26/12)) 
        
        # 4. Weekly Payment (52 times a year)
        WeeklyPayment = calculate_payment(self.weeklyinterestrate, n_months * (52/12)) 
        
        # 5. Rapid Bi-Weekly Payment (Monthly Payment / 2) 
        RapidBiweeklyPayment = MonthlyPayment / 2
        
        # 6. Rapid Weekly Payment (Monthly Payment / 4) - 
        RapidWeeklyPayment = MonthlyPayment / 4
        
        return (MonthlyPayment, SemiMonthlyPayment, BiweeklyPayment, 
                WeeklyPayment, RapidBiweeklyPayment, RapidWeeklyPayment)


    def generate_schedule(self):
        """
        (Part A New Functionality)
        Generates the loan payment schedule for the six options up to the loan term.
        Returns a dictionary of six Pandas DataFrames.
        """
        
        # Generates calculated payments
        payments = self.calculatepayments()
        payment_names = ['Monthly', 'Semi-Monthly', 'Bi-Weekly', 
                         'Weekly', 'Rapid Bi-Weekly', 'Rapid Weekly']
        payment_info = dict(zip(payment_names, payments))
        
        schedules = {} # Dictionary to hold the 6 DataFrames
        
        # Define the payment frequencies (payments per year)
        frequencies = {'Monthly': 12, 'Semi-Monthly': 24, 'Bi-Weekly': 26, 
                       'Weekly': 52, 'Rapid Bi-Weekly': 26, 'Rapid Weekly': 52}
        
        # Defines the periodic interest rates to use for interest calculation
        # Uses the respective periodic rate calculated in __init__
        rates = {'Monthly': self.monthlyinterestrate, 
                 'Semi-Monthly': self.semimonthlyinterestrate, 
                 'Bi-Weekly': self.biweeklyinterestrate, 
                 'Weekly': self.weeklyinterestrate, 
                 'Rapid Bi-Weekly': self.biweeklyinterestrate, 
                 'Rapid Weekly': self.weeklyinterestrate} 

        # Total number of payments in the Term
        total_term_payments = {}
        for name, freq in frequencies.items():
            total_term_payments[name] = self.term * freq
            
        # --- Schedule Generation Loop ---
        for name in payment_names:
            Pmt = payment_info[name] # Periodic payment amount
            Term_Periods = total_term_payments[name] # Total payments in the term
            Rate = rates[name] # Periodic interest rate

            # Initialize lists for the DataFrame columns
            period = []
            beginning_balance = []
            interest = []
            principal_paid = []
            ending_balance = []
            
            current_balance = self.principal
            
            for i in range(1, Term_Periods + 1):
                # Using NumPy to ensure efficient array like calculations 
                # Calculate Interest for the period: I = Beginning Balance * Periodic Rate
                I_Pmt = np.round(current_balance * Rate, 2)
                
                # Calculate Principal Paid: Principal = Payment - Interest
                Principal_Pmt = np.round(Pmt - I_Pmt, 2)
                
                # Check for final payment adjustment
                if current_balance - Principal_Pmt < 0:
                    Principal_Pmt = current_balance # Pay off remaining balance
                    Ending_Bal = 0.0
                else:
                    Ending_Bal = np.round(current_balance - Principal_Pmt, 2)
                
                # Store the results for the period
                period.append(i)
                beginning_balance.append(np.round(current_balance, 2))
                interest.append(I_Pmt)
                principal_paid.append(Principal_Pmt)
                ending_balance.append(Ending_Bal)
                
                # Update the balance for the next period
                current_balance = Ending_Bal
                
                if current_balance <= 0.0:
                    break
            
            # Create a Pandas DataFrame for the current payment schedule
            df = pd.DataFrame({
                'Period': period,
                'Beginning Balance': beginning_balance,
                'Payment': [np.round(Pmt, 2)] * len(period), # Keep the payment constant
                'Interest Paid': interest,
                'Principal Paid': principal_paid,
                'Ending Balance': ending_balance
            })
            
            schedules[name] = df
            
        return schedules

# --- Script Execution ---

def main():
    # Q1:Code to also prompt the user for the term of the mortgage.
    print("--- Loan Amortization and Payment Schedule Generator ---")
    try:
        principal = float(input("Enter the Principal Loan Amount (e.g., 100000): "))
        interestrate = float(input("Enter the Yearly Interest Rate (e.g., 5.5): "))
        amortization_period = int(input("Enter the Amortization Period in years (e.g., 25): "))
        # User input for the Term
        term = int(input("Enter the Term of the mortgage in years (e.g., 5): "))
        
    except ValueError:
        print("Invalid input. Please enter numbers for all values.")
        return
    
    # Create an instance of the class
    mortgage_calc = MortgagePaymentCalculator(principal, interestrate, amortization_period, term)
    
    # 1. Generate the six DataFrames
    print("\nCalculating Payment Schedules...")
    loan_schedules = mortgage_calc.generate_schedule()
    
    # 2. Exporting all six DataFrames to a single Excel file (Part A: Correct Excel)
    excel_filename = 'Loan_Amortization_Schedules.xlsx'
    
    # Using Pandas ExcelWriter to write to multiple sheets
    with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
        for name, df in loan_schedules.items():
            # Save each DataFrame to a separate worksheet labelled appropriately
            df.to_excel(writer, sheet_name=name, index=False)
            
            # (Formatting for Excel)
            worksheet = writer.sheets[name]
            # Setting column widths for better readability in Excel
            worksheet.set_column('A:F', 18) 
            
    print(f"Excel file saved: {excel_filename}")
    
    # 3. Generate a single graph depicting loan balance decline (Part A: Functional Code & Matplotlib)
    plt.figure(figsize=(12, 7)) # Setted plot size
    
    # Plot Ending Balance over periods for all six schedules
    for name, df in loan_schedules.items():
        # The x-axis should represent time, which is the Period column
        plt.plot(df['Period'], df['Ending Balance'], label=f'{name} ({df.iloc[-1]["Period"]} payments)')

    # --- Plot Formatting ---
    plt.title(f'Loan Balance Decline Over Term (Rate: {interestrate}%, Principal: ${principal:,.2f})')
    plt.xlabel(f'Payment Period (over a {term}-year Term)')
    plt.ylabel('Ending Loan Balance ($)')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # We six payment options & must create six data frames.
    # Using the savefig(...) function within Matplotlib to save the graph as a PNG file.
    plt.legend(title="Payment Options", loc='upper right')
    
    # Set y-axis to start from 0 for better visualization of decline
    plt.ylim 
    
    png_filename = 'Loan_Balance_Decline.png'
    plt.savefig(png_filename)
    plt.close() 
    
    print(f"✅ PNG file saved: {png_filename}")

if __name__ == "__main__":
    main()
