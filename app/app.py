#!/usr/bin/env python3
import os

from Database.kinase_functions import *
from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from forms import *
from user_data_input_parameters import *
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = '11d5c86229d773022cb61679343f8232'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title= "Welcome to PhosphoView")


ALLOWED_EXTENSIONS = {'tsv', 'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=['GET', 'POST'])
def Data_Upload():
    form=FileForm()
    if request.method == "POST":
            if request.files:
                InputFile = request.files["InputFile"]
                if InputFile.filename == '':
                    flash('No selected file', 'danger')
                    return redirect(url_for('Data_Upload'))
                if InputFile and allowed_file(InputFile.filename):
                    filename = secure_filename(InputFile.filename)
                    uploads_dir = os.path.join(app.instance_path, 'Data_Upload')
                    if not os.path.exists(uploads_dir):
                        os.makedirs(uploads_dir)
                    InputFile.save(os.path.join(uploads_dir, secure_filename(InputFile.filename)))
                    flash ("Upload Successful", "info")
                    return redirect(url_for('Parameter', filename=filename ))
                else:
                    flash('Incorrect selected file', 'danger')
    return render_template('Data_Upload.html', title='Data Upload', form=form)

#after the data is uploaded, this is the parameter page it is redirected to
@app.route("/upload/Parameters/<filename>", methods = ['GET', 'POST'])
def Parameter(filename):
    form = Parameters()  
    if request.method == "POST": #if it is submitted
        PValue = form.PValue.data  #user p-value
        Fold = form.Fold.data    #user fold value
        Coeff = form.Coefficience.data  #user coeff value 
        Sub = form.Sub.data   #user number of substrates

        if 0 <= PValue <= 0.05:  #if the pvalue is with 0-0.05
            if 0 <= Coeff <= 3:  # and coeff is within 0-3 , take use to Visualisation
                return redirect(url_for('Visualisation', filename=filename, PValue=PValue, Fold=Fold, Coeff=Coeff, Sub=Sub ))
            else:
                flash("Coefficience of Variance Threshold must be a whole number between 0 to 3", "danger") 


        else:
            flash("P-Value Threshold must be between 0 - 0.05", "danger")
    return render_template('data_parameter.html', form=form)

# this is the final data analysis results page 
@app.route("/upload/Parameters/<filename>/<PValue>/<Fold>/<Coeff>/<Sub>")
def Visualisation(filename, PValue, Fold, Coeff, Sub):
    calculations_df,df_final2,df_final3=data_analysis(filename, PValue, Coeff, Sub)
    VolcanoPlot1 = VolcanoPlot_Sub(df_final2,PValue, Fold, Coeff) #outputs one volcano plot
    VolcanoPlot2 = VolcanoPlot(df_final3, PValue, Fold,Coeff)  #outputs another volcano plot
    Enrichment = EnrichmentPlot(calculations_df, PValue, Fold, Coeff, Sub)  #outputs enrichment plot
    Calculations= df2_html(calculations_df)  #outputs a table of information
    return render_template('data_analysis_results.html',filename=filename, PValue=PValue, Fold=Fold, Coeff=Coeff, Sub=Sub, VolcanoPlot1=VolcanoPlot1, VolcanoPlot2=VolcanoPlot2, Enrichment=Enrichment,Calculations=Calculations)

#human kinase search page
@app.route("/HumanKinases", methods = ['GET', 'POST'])
def HumanKinases():
    form=Kinase() 
    search_kinase = form.search.data
    list_aliases = get_all_aliases() #this function returns a list of all kinase aliases

    if form.validate_on_submit():  
        for x in range(len(list_aliases)):  
            if search_kinase.upper() in list_aliases[x]:  #if user input in our list, redirect to results page. 
                return redirect(url_for('results_kinases', search_kinase=search_kinase))

        else:
            flash('Kinase not found. Please check and try again.', 'danger')
    
    return render_template('HumanKinases.html', title='List of Human Kinases', form=form)
      
#Kinase results page 
@app.route("/HumanKinases/results_kinases/<search_kinase>")
def results_kinases(search_kinase):
    dictionary = get_gene_alias_protein_name(search_kinase)  #outputs a dictionary of information that matches the user input
    return render_template('results_kinases.html', dictionary=dictionary, search_kinase=search_kinase)

#Individual kinase page from the gene link in results_kinases.html.
@app.route("/HumanKinases/results_kinases/<search_kinase>/<gene>")
def Individual_kinase(search_kinase,gene):  
    Information = get_gene_metadata_from_gene(gene)    
    subcellular_location = (get_subcellular_location_from_gene(gene))
    substrate_phosphosites = get_substrates_phosphosites_from_gene(gene)
    Inhibitor = get_inhibitors_from_gene(gene)
    return render_template('Individual_kinase.html', title='Individual Kinase Page', Inhibitor= Inhibitor, gene = gene, Information = Information, subcellular_location= subcellular_location, substrate_phosphosites=substrate_phosphosites)

#same individual kinase page but this is from the the link in inhibitors.html page 
@app.route("/<gene>")
def kinase_from_inhibitor_page(gene):
    Information = get_gene_metadata_from_gene(gene)
    subcellular_location = (get_subcellular_location_from_gene(gene))
    substrate_phosphosites = get_substrates_phosphosites_from_gene(gene)
    Inhibitor = get_inhibitors_from_gene(gene)
    return render_template('Individual_kinase.html', title='Individual Kinase Page', Inhibitor= Inhibitor, gene = gene, Information = Information, subcellular_location= subcellular_location, substrate_phosphosites=substrate_phosphosites)


@app.route("/Phosphosite", methods= ['GET', 'POST'])
def Phosphosites():  
    Phospho_form = Phosphosite()
    Substrate_form = Substrate()

    Phospho_form.chromosome.choices = get_all_chromosome()

    if request.method == "POST":
        if Substrate_form.validate_on_submit():
            substrate_input = Substrate_form.search.data.upper()
            if substrate_input in get_all_substrates():      # if user input is found in our list of substrates, redirect to results page for substrate.
                return redirect(url_for('results_by_substrate',substrate_input=substrate_input) )
            else:
                flash("Not valid substrate name", "danger")
                return redirect(url_for('Phosphosites'))

        if Phospho_form.validate_on_submit() == False:
            chr_number = Phospho_form.chromosome.data
            kar_input = Phospho_form.karyotype.data
            kar_inputs = kar_input.replace(" ", "")
            if kar_inputs:             #if there is a value in karyotype form, redirec to results page for that chromosome and karyotype
                flash('Submitted Chromosome: '+ chr_number + ' and Karyotype '+ kar_inputs, 'info')
                return redirect(url_for('results_phosphosite2', chr_number=chr_number,kar_inputs=kar_inputs ))

    return render_template('Phosphosite.html', title='Phosphosite Search', Substrate_form=Substrate_form, Phospho_form=Phospho_form)

#this function is used in the Phosphosite search page, first the user inputs chromosome and according to that it returns the karyotype. 
@app.route("/karyotype/<chromosome>")
def karyotype(chromosome):
    karyotypes = get_karyotype_through_chromosome(chromosome)
    return jsonify({'karyotypes': karyotypes})


#function used after user inputs valid name in the substrate search bar
@app.route("/Phosphosite_result/<substrate_input>")
def results_by_substrate(substrate_input): 
    substrate_info = get_substrate_phosphosites_from_substrate(substrate_input)
    return render_template('results_phosphosite.html', substrate_info=substrate_info)

#function used after user celects a chromosome and an karyotype
@app.route("/Phosphosite_result/<chr_number>/<kar_inputs>")
def results_phosphosite2(chr_number,kar_inputs):
    Info_by_chromosome_karyotype = get_sub_pho_from_chr_kar_loc(chr_number ,kar_inputs)
    return render_template('results_phosphosite_location.html', Info_by_chromosome_karyotype=Info_by_chromosome_karyotype,chr_number=chr_number,kar_inputs=kar_inputs )

#inhibitor search page
@app.route("/Inhibitors", methods = ['GET', 'POST'])
def Inhibitors():  
    ALL_inhibitors = get_all_inhibitors_meta()
    return render_template('inhibitors.html', title='Inhibitors', ALL_inhibitors=ALL_inhibitors)

@app.route("/Inhibitors/<inhibitor>")
def Individual_Inhibitors(inhibitor):
    Individual_Inhibitor = get_inhibitor_meta_from_inhibitor(inhibitor)
    return render_template('Individual_inhibitor.html', title='Individual Inhibitors', Individual_Inhibitor=Individual_Inhibitor, inhibitor=inhibitor)

@app.route("/help")
def Help():
    return render_template('help.html', title='Help')


@app.route("/about")
def about():

    return render_template('about.html', title = " About")




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

