# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 11:05:57 2024

@author: gangylee

@Features Summary
1. Profile Tab:
    - Save user details.
    - Calculate BMI with feedback.
    
2. Workout Plan Tab:
    - Add and view workout schedules.
    
3. Calorie Tracker Tab:
    - Log meals with calorie counts.
    
4. Reports Tab:
    - Visualize calorie trends with matplotlib.
    - Export calorie data to CSV.

"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import matplotlib.pyplot as plt
from datetime import date
import csv

# Initialize Database
def init_db():
    conn = sqlite3.connect('fitness.db')
    cursor = conn.cursor()
    
    # User table
    cursor.execute('''CREATE TABLE IF NOT EXISTS user (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        age INTEGER,
                        weight REAL,
                        height REAL
                      )''')
    # Calories table
    cursor.execute('''CREATE TABLE IF NOT EXISTS calories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        meal TEXT,
                        calories INTEGER
                      )''')
    # Workout table
    cursor.execute('''CREATE TABLE IF NOT EXISTS workout (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        workout TEXT,
                        duration INTEGER
                      )''')
    conn.commit()
    conn.close()

# Main Application Class
class FitnessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fitness Plan and Calorie Tracker")
        self.root.geometry("900x700")
        
        # Tabs
        self.tab_control = ttk.Notebook(root)
        self.profile_tab = ttk.Frame(self.tab_control)
        self.plan_tab = ttk.Frame(self.tab_control)
        self.tracker_tab = ttk.Frame(self.tab_control)
        self.report_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.profile_tab, text='Profile')
        self.tab_control.add(self.plan_tab, text='Workout Plan')
        self.tab_control.add(self.tracker_tab, text='Calorie Tracker')
        self.tab_control.add(self.report_tab, text='Reports')
        self.tab_control.pack(expand=1, fill="both")
        
        self.create_profile_tab()
        self.create_plan_tab()
        self.create_tracker_tab()
        self.create_report_tab()
    
    # Profile Tab
    def create_profile_tab(self):
        tk.Label(self.profile_tab, text="Name").grid(row=0, column=0, padx=10, pady=10)
        self.name_entry = tk.Entry(self.profile_tab)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(self.profile_tab, text="Age").grid(row=1, column=0, padx=10, pady=10)
        self.age_entry = tk.Entry(self.profile_tab)
        self.age_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(self.profile_tab, text="Weight (kg)").grid(row=2, column=0, padx=10, pady=10)
        self.weight_entry = tk.Entry(self.profile_tab)
        self.weight_entry.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(self.profile_tab, text="Height (cm)").grid(row=3, column=0, padx=10, pady=10)
        self.height_entry = tk.Entry(self.profile_tab)
        self.height_entry.grid(row=3, column=1, padx=10, pady=10)
        
        tk.Button(self.profile_tab, text="Save Profile", command=self.save_profile).grid(row=4, column=0, columnspan=2, pady=10)
        tk.Button(self.profile_tab, text="Calculate BMI", command=self.calculate_bmi).grid(row=5, column=0, columnspan=2, pady=10)
    
    def save_profile(self):
        name = self.name_entry.get()
        age = self.age_entry.get()
        weight = self.weight_entry.get()
        height = self.height_entry.get()
        
        if not (name and age and weight and height):
            messagebox.showerror("Error", "Please fill out all fields.")
            return
        
        conn = sqlite3.connect('fitness.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user (name, age, weight, height) VALUES (?, ?, ?, ?)", (name, age, weight, height))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", "Profile saved!")
    
    def calculate_bmi(self):
        try:
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get()) / 100  # Convert to meters
            bmi = weight / (height ** 2)
            category = ("Underweight", "Normal weight", "Overweight", "Obese")
            index = min(max(int((bmi - 18.5) / 5), 0), 3)
            messagebox.showinfo("BMI Calculation", f"Your BMI is {bmi:.2f} ({category[index]}).")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid weight and height.")
    
    # Workout Plan Tab
    def create_plan_tab(self):
        tk.Label(self.plan_tab, text="Workout").grid(row=0, column=0, padx=10, pady=10)
        self.workout_entry = tk.Entry(self.plan_tab)
        self.workout_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(self.plan_tab, text="Duration (mins)").grid(row=1, column=0, padx=10, pady=10)
        self.duration_entry = tk.Entry(self.plan_tab)
        self.duration_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Button(self.plan_tab, text="Add Workout", command=self.add_workout).grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(self.plan_tab, text="View Plan", command=self.view_workout_plan).grid(row=3, column=0, columnspan=2, pady=10)
    
    def add_workout(self):
        workout = self.workout_entry.get()
        duration = self.duration_entry.get()
        today = date.today().strftime('%Y-%m-%d')
        
        if not (workout and duration.isdigit()):
            messagebox.showerror("Error", "Please enter valid data.")
            return
        
        conn = sqlite3.connect('fitness.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO workout (date, workout, duration) VALUES (?, ?, ?)", (today, workout, int(duration)))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", "Workout added!")
    
    def view_workout_plan(self):
        conn = sqlite3.connect('fitness.db')
        cursor = conn.cursor()
        cursor.execute("SELECT date, workout, duration FROM workout ORDER BY date")
        data = cursor.fetchall()
        conn.close()
        
        plan_window = tk.Toplevel(self.root)
        plan_window.title("Workout Plan")
        plan_window.geometry("400x300")
        
        text = tk.Text(plan_window)
        text.pack(expand=True, fill="both")
        for row in data:
            text.insert(tk.END, f"{row[0]}: {row[1]} ({row[2]} mins)\n")
    
    # Calorie Tracker Tab
    def create_tracker_tab(self):
        tk.Label(self.tracker_tab, text="Meal").grid(row=0, column=0, padx=10, pady=10)
        self.meal_entry = tk.Entry(self.tracker_tab)
        self.meal_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(self.tracker_tab, text="Calories").grid(row=1, column=0, padx=10, pady=10)
        self.calories_entry = tk.Entry(self.tracker_tab)
        self.calories_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Button(self.tracker_tab, text="Add Entry", command=self.add_calorie_entry).grid(row=2, column=0, columnspan=2, pady=10)
    
    def add_calorie_entry(self):
        meal = self.meal_entry.get()
        calories = self.calories_entry.get()
        today = date.today().strftime('%Y-%m-%d')
        
        if not (meal and calories.isdigit()):
            messagebox.showerror("Error", "Please enter valid data.")
            return
        
        conn = sqlite3.connect('fitness.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO calories (date, meal, calories) VALUES (?, ?, ?)", (today, meal, int(calories)))
        conn.commit()
        conn.close()
        
        messagebox.showinfo("Success", "Entry added!")
    
    # Reports Tab
    def create_report_tab(self):
        tk.Button(self.report_tab, text="Calorie Report", command=self.view_calorie_report).grid(row=0, column=0, padx=10, pady=10)
        tk.Button(self.report_tab, text="Export Data", command=self.export_data).grid(row=1, column=0, padx=10, pady=10)
    
    def view_calorie_report(self):
        conn = sqlite3.connect('fitness.db')
        cursor = conn.cursor()
        cursor.execute("SELECT date, SUM(calories) FROM calories GROUP BY date")
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            messagebox.showinfo("Info", "No data to display.")
            return
        
        dates = [row[0] for row in data]
        calories = [row[1] for row in data]
        
        plt.figure(figsize=(10, 5))
        plt.bar(dates, calories, color='blue')
        plt.xlabel("Date")
        plt.ylabel("Calories")
        plt.title("Calorie Intake Over Time")
        plt.show()
    
    def export_data(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        
        conn = sqlite3.connect('fitness.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM calories")
        data = cursor.fetchall()
        conn.close()
        
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Date", "Meal", "Calories"])
            writer.writerows(data)
        
        messagebox.showinfo("Success", "Data exported successfully!")

# Run Application
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = FitnessApp(root)
    root.mainloop()
