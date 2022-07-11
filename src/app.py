from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import validators, DecimalField, SelectField, SubmitField
from engine import Engine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'karşıkidağdabirtırtılyaprakyiyorhıtırhırıthaintırtılpistırtılortadanikiyeyırtıl'
Bootstrap(app)

app.config['BOOTSTRAP_SERVE_LOCAL'] = True

engine = Engine()

class Loan(FlaskForm):
    amount = DecimalField('Tutar:', validators=[validators.DataRequired(),
                                             validators.NumberRange(min=500, max=500000, 
                                                                    message='500-500000 TL Arası giriş yapılabilir')])
    maturity = SelectField(u'Vade', choices=[('3', '3 Ay'), ('6', '6 ay'), ('9', '9 Ay'), 
                                             ('12', '12 Ay'), ('18', '18 Ay'), ('24', '24 Ay'), 
                                             ('30', '30 Ay'), ('32', '32 Ay'), ('36', '36 Ay')])
    submit = SubmitField('Hesapla')
    
class Deposit(FlaskForm):
    amount = DecimalField('Tutar:', validators=[validators.DataRequired(),
                                             validators.NumberRange(min=500, max=9999999, 
                                                                    message='500-9999999 TL Arası giriş yapılabilir')])
    maturity =  SelectField(u'Vade', choices=[('32', '32 Gün'), ('46', '46 Gün'), ('55', '55 Gün'), 
                                             ('92', '92 Gün'), ('181', '181 Gün')])
    submit = SubmitField('Hesapla')    

@app.route('/', methods=['GET', 'POST'])
@app.route('/loan.html', methods=['GET', 'POST'])
def loan():
    form = Loan()
    message = []
    if form.validate_on_submit():
        amount = int(form.amount.data)
        maturity = int(form.maturity.data)
        if amount>100000 and maturity>12:
            message = ["100000TL üzeri tüketici kredileri maksimum 12 ay vade ile sınırlıdır."]
        elif 50000 < amount <=100000 and maturity>24:
            message = ["50000TL-100000TL(dahil) aralığı tüketici kredileri maksimum 24 ay vade ile sınırlıdır."]
        else:
            result = engine.calculate_loan(amount,maturity)
            
            if result.shape[0]>0:
                for idx,row in result.iterrows():
                    message.append("Banka: "+ row['bank'].replace('-',' ').upper() + 
                                   " / Faiz Oranı: %" + str(row['interest_rate']) +
                                   " / Aylık Taksit: " + str(int(row['monthly_payment'])) + "TL" +
                                   " / Tahsis Ücreti: " + str(int(row['total_fee'])) + "TL" +
                                   " / Toplam Maliyet: " + str(int(row['total_cost'])) + "TL")
            else:
                message = ["Seçilen tutar ve/veya vade süresi uygun değil."]              
    return render_template('loan.html', form=form, message=message)

@app.route('/deposit.html', methods=['GET', 'POST'])
def deposit():
    form = Deposit()
    message = []
    if form.validate_on_submit():
        amount = int(form.amount.data)
        maturity = int(form.maturity.data)
        result = engine.calculate_interests(amount,maturity)
        
        if result.shape[0]>0:
            for idx,row in result.iterrows():
                message.append("Banka: "+ row['bank'].replace('-',' ').upper() + 
                               " / Faiz Oranı: %" + str(row['interest_rate']) + 
                               " / Toplam Getiri: " + str((float(row['interest_rate'])*amount*maturity)/36500) + "TL")
        else:
            message = ["Seçilen tutar ve/veya vade süresi uygun değil."]
    return render_template('deposit.html', form=form, message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=False)