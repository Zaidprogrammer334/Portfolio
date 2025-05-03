import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import logging
from urllib.parse import quote

class AllSportsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("معلومات الفريق - AllSportsAPI")
        self.root.geometry("800x650")
        
        # إعداد نظام التسجيل للأخطاء
        logging.basicConfig(
            filename='football_app.log',
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # مفتاح API - استبدله بمفتاحك الصحيح من AllSportsAPI
        self.api_key = "90ef223499837e560f288bbe118d19af1126a240def36891a8feefdb4e4f912b"  # احصل عليه من https://allsportsapi.com/
        self.base_url = "https://allsportsapi.com/api/football/"
        
        # إعداد الواجهة
        self.setup_ui()
        
        # تعطيل الزر أثناء التحميل
        self.search_button.config(state=tk.DISABLED)
        self.root.after(100, self.check_api_connection)
    
    def setup_ui(self):
        # إطار البحث
        search_frame = ttk.Frame(self.root, padding="10")
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="اسم الفريق:").pack(side=tk.LEFT)
        self.team_entry = ttk.Entry(search_frame, width=35)
        self.team_entry.pack(side=tk.LEFT, padx=5)
        self.team_entry.bind("<Return>", lambda e: self.search_team())
        
        self.search_button = ttk.Button(search_frame, text="بحث", command=self.search_team)
        self.search_button.pack(side=tk.LEFT, padx=5)
        
        # زر التحديث
        ttk.Button(search_frame, text="تحديث البيانات", command=self.refresh_data).pack(side=tk.RIGHT)
        
        # إطار حالة الاتصال
        self.connection_status = ttk.Label(self.root, text="جاري التحقق من اتصال API...", foreground="blue")
        self.connection_status.pack(fill=tk.X, padx=10, pady=5)
        
        # إطار النتائج
        self.results_frame = ttk.LabelFrame(self.root, text="معلومات الفريق", padding="15")
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # معلومات الفريق الأساسية
        info_frame = ttk.Frame(self.results_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.team_info = {
            "الاسم": ttk.Label(info_frame, text="", font=('Arial', 10, 'bold')),
            "الدولة": ttk.Label(info_frame, text=""),
            "المدرب": ttk.Label(info_frame, text=""),
            "الملعب": ttk.Label(info_frame, text=""),
            "سعة الملعب": ttk.Label(info_frame, text=""),
            "المدينة": ttk.Label(info_frame, text=""),
            "آخر تحديث": ttk.Label(info_frame, text="")
        }
        
        for i, (label, widget) in enumerate(self.team_info.items()):
            ttk.Label(info_frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            widget.grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)
        
        # اللاعبين
        ttk.Label(self.results_frame, text="اللاعبون:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=5)
        
        self.players_tree = ttk.Treeview(
            self.results_frame,
            columns=("number", "name", "position", "age", "nationality", "goals"),
            show="headings",
            height=15
        )
        
        # تعريف العناوين
        columns = {
            "number": {"text": "الرقم", "width": 50, "anchor": "center"},
            "name": {"text": "الاسم", "width": 180},
            "position": {"text": "المركز", "width": 100},
            "age": {"text": "العمر", "width": 50, "anchor": "center"},
            "nationality": {"text": "الجنسية", "width": 100},
            "goals": {"text": "الأهداف", "width": 60, "anchor": "center"}
        }
        
        for col, config in columns.items():
            self.players_tree.heading(col, text=config["text"])
            self.players_tree.column(col, width=config["width"], anchor=config.get("anchor", "w"))
        
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.players_tree.yview)
        self.players_tree.configure(yscrollcommand=scrollbar.set)
        
        self.players_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # إطار التحميل
        self.loading_frame = ttk.Frame(self.root)
        self.loading_label = ttk.Label(self.loading_frame, text="جاري تحميل البيانات...", foreground="green")
        self.loading_label.pack()
        self.loading_frame.pack_forget()
    
    def check_api_connection(self):
        """التحقق من اتصال API"""
        try:
            test_url = f"{self.base_url}?met=Leagues&APIkey={self.api_key}"
            response = requests.get(test_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == 1:
                    self.connection_status.config(text="اتصال API نشط", foreground="green")
                    self.search_button.config(state=tk.NORMAL)
                    return True
                else:
                    error_msg = data.get("message", "فشل الاتصال بالخادم")
                    self.connection_status.config(text=f"خطأ: {error_msg}", foreground="red")
            else:
                self.connection_status.config(text=f"خطأ في الاتصال: {response.status_code}", foreground="red")
            
            self.search_button.config(state=tk.DISABLED)
            return False
            
        except requests.exceptions.RequestException as e:
            self.connection_status.config(text=f"فشل الاتصال: {str(e)}", foreground="red")
            self.search_button.config(state=tk.DISABLED)
            return False
    
    def show_loading(self, show=True):
        """عرض/إخفاء مؤشر التحميل"""
        if show:
            self.loading_frame.pack(fill=tk.X, pady=5)
            self.root.update()
        else:
            self.loading_frame.pack_forget()
    
    def search_team(self):
        """البحث عن فريق"""
        team_name = self.team_entry.get().strip()
        if not team_name:
            messagebox.showwarning("تحذير", "الرجاء إدخال اسم الفريق")
            return
        
        if not self.check_api_connection():
            messagebox.showerror("خطأ", "لا يوجد اتصال بخدمة API")
            return
        
        self.show_loading(True)
        
        try:
            # ترميز اسم الفريق للرابط URL
            encoded_team = quote(team_name)
            search_url = f"{self.base_url}?met=Teams&teamName={encoded_team}&APIkey={self.api_key}"
            
            response = requests.get(search_url, timeout=15)
            
            if response.status_code == 404:
                messagebox.showerror("خطأ", "لم يتم العثور على الفريق. تأكد من صحة الاسم")
                return
                
            response.raise_for_status()
            data = self.check_api_response(response)
            
            if data.get("success") != 1:
                messagebox.showerror("خطأ", f"خطأ من الخادم: {data.get('message', 'Unknown error')}")
                return
                
            if not data.get("result"):
                messagebox.showerror("خطأ", "لم يتم العثور على الفريق")
                return
                
            team_id = data["result"][0]["team_key"]
            self.get_team_details(team_id)
            
        except requests.exceptions.Timeout:
            messagebox.showerror("خطأ", "انتهت مهلة الاتصال بالخادم")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("خطأ", f"فشل الاتصال: {str(e)}")
        except ValueError as e:
            messagebox.showerror("خطأ", str(e))
        except Exception as e:
            logging.error(f"Error in search_team: {str(e)}")
            messagebox.showerror("خطأ", "حدث خطأ غير متوقع")
        finally:
            self.show_loading(False)
    
    def check_api_response(self, response):
        """فحص صحة استجابة API"""
        try:
            if not response.content:
                raise ValueError("استجابة فارغة من الخادم")
            
            data = response.json()
            
            if "success" not in data:
                raise ValueError("استجابة غير متوقعة من الخادم")
                
            return data
            
        except json.JSONDecodeError as e:
            error_msg = f"خطأ في تحليل JSON: {str(e)}\n"
            error_msg += f"الاستجابة الخام: {response.text[:200]}..."
            raise ValueError(error_msg)
    
    def get_team_details(self, team_id):
        """جلب تفاصيل الفريق واللاعبين"""
        try:
            self.show_loading(True)
            
            team_url = f"{self.base_url}?met=Teams&teamId={team_id}&APIkey={self.api_key}"
            players_url = f"{self.base_url}?met=Players&teamId={team_id}&APIkey={self.api_key}"
            
            # جلب بيانات الفريق
            team_response = requests.get(team_url, timeout=15)
            team_data = self.check_api_response(team_response)
            
            if team_data["success"] == 1 and team_data.get("result"):
                team = team_data["result"][0]
                
                self.team_info["الاسم"].config(text=team.get("team_name", "غير معروف"))
                self.team_info["الدولة"].config(text=team.get("team_country", "غير معروف"))
                
                # جلب اسم المدرب
                coach_name = "غير معروف"
                if team.get("coaches"):
                    coach_name = team["coaches"][0].get("coach_name", "غير معروف")
                self.team_info["المدرب"].config(text=coach_name)
                
                # معلومات الملعب
                venue = team.get("venue", {})
                self.team_info["الملعب"].config(text=venue.get("venue_name", "غير معروف"))
                self.team_info["سعة الملعب"].config(text=str(venue.get("venue_capacity", "غير معروف")))
                self.team_info["المدينة"].config(text=venue.get("venue_city", "غير معروف"))
                self.team_info["آخر تحديث"].config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            # جلب بيانات اللاعبين
            players_response = requests.get(players_url, timeout=15)
            players_data = self.check_api_response(players_response)
            
            # مسح اللاعبين السابقين
            for item in self.players_tree.get_children():
                self.players_tree.delete(item)
            
            if players_data["success"] == 1 and players_data.get("result"):
                for player in players_data["result"]:
                    self.players_tree.insert("", tk.END, values=(
                        player.get("player_number", "-"),
                        player.get("player_name", "غير معروف"),
                        player.get("player_type", "غير معروف"),
                        player.get("player_age", "-"),
                        player.get("player_country", "غير معروف"),
                        player.get("player_goals", "-")
                    ))
        
        except requests.exceptions.Timeout:
            messagebox.showerror("خطأ", "انتهت مهلة الاتصال بالخادم")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("خطأ", f"فشل الاتصال: {str(e)}")
        except ValueError as e:
            messagebox.showerror("خطأ", str(e))
        except Exception as e:
            logging.error(f"Error in get_team_details: {str(e)}")
            messagebox.showerror("خطأ", "حدث خطأ غير متوقع")
        finally:
            self.show_loading(False)
    
    def refresh_data(self):
        """تحديث البيانات الحالية"""
        current_team = self.team_entry.get().strip()
        if current_team:
            self.search_team()
        else:
            messagebox.showinfo("تحديث", "لا يوجد فريق معروض للتحديث")

if __name__ == "__main__":
    from datetime import datetime
    root = tk.Tk()
    app = AllSportsApp(root)
    root.mainloop()