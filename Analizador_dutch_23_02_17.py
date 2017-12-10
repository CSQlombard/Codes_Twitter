import csv
import operator
##from matplotlib import pyplot as plt
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
##import datetime
##import matplotlib
import matplotlib.dates as mdates

def analizando():
    #file = open("api_sentiment_dutch.txt",'r')
    file = open("sentiment_output_dutch_stream.txt",'r')
    reader = csv.reader(file, dialect ='excel', delimiter ='\t')
    dictionary = {}
    lista_de_partidos = []
    lista_de_partidos.append(["'mark'", "'rutte'", "'vvd'"])
    lista_de_partidos.append(["'geert'", "'wilders'", "'pvv'"])
    lista_de_partidos.append(["'emile'", "'roemer'", "'sp'"])
    lista_de_partidos.append(["'sybrand'", "'haersma'", "'buma'", "'cda'"])
    lista_de_partidos.append(["'lodewijk'", "'asscher'", "'pvda'"])
    lista_de_partidos.append(["'jesse'", "'klaver'", "'gl'"])
    lista_de_partidos.append(["'alexander'", "'pechtold'", "'d66'"])
    lista_de_partidos.append(["'gert'", "'jan'","'segers'", "'cu'"])
    lista_de_partidos.append(["'henk'", "'krol'", "'50plus'"])
    lista_de_partidos.append(["'marianne'", "'thieme'", "'pvdd'"])
    lista_de_partidos.append(["'kees'", "'staaij'", "'sgp'"])

    for row in reader:
        lista = row[3:-2]
        for item in lista_de_partidos:
            if item[0] in lista or item[1] in lista or item[2] in lista:
                key = item[2][1:-1]
                if key in dictionary:
                    dictionary[key].append((row[0], row[1], row[2]))
                else:
                    dictionary[key] = []
                    dictionary[key].append((row[0], row[1], row[2]))

    file.close()
    return dictionary

def otro_contador(dictionary, tbin, ini_time, partido):

    information = []
    sentimiento = {}
    votes = {}

    for item in dictionary[partido]:
        information.append(item)
    s_information = sorted(information)

    min_time = s_information[0][0]
    max_time = s_information[-1][0]
    if ini_time:
        objeto_min = datetime.strptime(ini_time,'%Y-%m-%d %H:%M')
    else:
        objeto_min = datetime.strptime(min_time[0:16], '%Y-%m-%d %H:%M')

    objeto_max = datetime.strptime(max_time[0:16], '%Y-%m-%d %H:%M')
    diferencia = objeto_max - objeto_min
    diferencia_min = divmod(diferencia.days * 86400 + diferencia.seconds,60)
    ## diferencia en minutos
    c = 0
    while c <= diferencia_min[0] / int(tbin):

        time_bin_i1 = []
        time_bin_i1 = objeto_min + timedelta(0,60*int(tbin)*c)
        time_bin_i2 = []
        time_bin_i2 = objeto_min + timedelta(0,60*int(tbin)*(c+1))

        votes[time_bin_i1] = []
        votes[time_bin_i1].append(0)
        sentimiento[time_bin_i1] = []
        sentimiento[time_bin_i1].append(0)
        user_ids_times = []
        user_id = {}

        for i, item in enumerate(s_information):
            obj_time = datetime.strptime(item[0][0:16], '%Y-%m-%d %H:%M')
            if obj_time >= time_bin_i1 and obj_time < time_bin_i2:

                cont = 0
                for user_id_time in user_ids_times:
                    if item[1][1:] in user_id_time[1]:
                        cont += 1
                        print item[1][1:], item[0], user_id_time[0]

                if cont == 0:
                    user_ids_times.append((item[0], item[1][1:]))
                    sentimiento[time_bin_i1].append(float(item[2]))
                    if item[1][1:] in user_id:
                        user_id[time_bin_i1].append(1)
                    else:
                        user_id[time_bin_i1] = []
                        user_id[time_bin_i1].append(1)

                    if float(item[2]) > 0:# and time_bin_i1 in votes:
                        votes[time_bin_i1].append(1)

        c += 1

        for item in user_id.keys():
            contador = 0
            contador = sum(user_id[item])
            if contador > 1:
                print item
                #with open('strange_users.txt', 'a') as f:
                #    f.write("%r\t\n" % str(item))

    return votes, sentimiento

def plot_votes(votes,tbin,partido,nombres_partidos,total_votes,modo2):

    plot_output = 0
    output = {}
    for key in votes.keys():
        output[key] = []
        output[key].append(sum(votes[key]))

    sorted_output = {}
    sorted_output = sorted(output.items(), key = operator.itemgetter(0))

    final_list_x = []
    final_list_y = []
    final_list_x = [item[0] for item in sorted_output]
    final_list_y = [item[1] for item in sorted_output]

    final_list_x_2 = []
    for i, _ in enumerate(final_list_x):
        final_list_x_2.append(final_list_x[i] + timedelta(0,60*60))

    if len(final_list_y) == 1:
        plot_output = 1
        for i,item in enumerate(nombres_partidos):
            if partido == item[0]:
                if modo2 == 'all':
                    perc = 0
                    perc = 100*float(final_list_y[0][0])/float(total_votes)
                    plt.bar(i,perc, color=item[1])
                else:
                    plt.bar(i,final_list_y[0][0], color=item[1])
    else:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d-%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=2*tbin))
        for i,item in enumerate(nombres_partidos):
            if partido == item[0]:
                plt.plot(final_list_x_2, final_list_y, color = item[1], marker ='o', linestyle ='solid',label=item[0])#

        plt.gcf().autofmt_xdate()
        plt.xlabel("Day - Time")

    if modo2 == 'all':
        plt.ylabel("perc Votes")
    else:
        plt.ylabel("# Votes")

    plt.title("Votes")
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    return plt, plot_output

def plot_sentimientos(sentimiento,tbin,partido,nombres_partidos,modo2):
    output = {}
    for key in sentimiento.keys():
        output[key] = []
        if modo2 == 'suma':
            output[key].append(sum(sentimiento[key]))
        else:
            total_pos = 0.0
            total_neg = 0.0
            for value in sentimiento[key]:
                if float(value) > 0:
                    total_pos += float(value)
                if float(value) <0:
                    total_neg += float(value)

            if modo2 == 'pos':
                output[key].append(total_pos)
            if modo2 == 'neg':
                output[key].append(total_neg)

    sorted_output = {}
    sorted_output = sorted(output.items(), key = operator.itemgetter(0))

    final_list_x = []
    final_list_y = []
    final_list_x = [item[0] for item in sorted_output]
    final_list_y = [item[1] for item in sorted_output]

    final_list_x_2 = []
    for i, _ in enumerate(final_list_x):
        final_list_x_2.append(final_list_x[i] + timedelta(0,60*60))

    ##customdate = datetime(2016,1,1,int(final_list_x[0][0:2])-1, int(final_list_x[0][3:5]))
    ##x = [final_list_x[0] + timedelta(minutes=i) for i in range(len(final_list_y))]
    ##dates = matplotlib.dates.date2num(final_list_x_2)
    ##matplotlib.pyplot.plot_date(dates,final_list_y)## color = 'green', marker ='o', linestyle ='solid')
    #f, ax = plt.subplots()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d-%H:%M'))
    #plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=2*tbin))
    for i,item in enumerate(nombres_partidos):
        if partido == item[0]:
            plt.plot(final_list_x_2, final_list_y, color = item[1], marker ='o', linestyle ='solid',label=item[0])#

    if modo2 == "suma":
        plt.ylabel("Sum Sentiments")
    if modo2 == "pos":
        plt.ylabel("Sum Positive Sentiments")
    if modo2 == "neg":
        plt.ylabel("Sum Negative Sentiments")

    plt.xlabel("Day - Time")
    #plt.title("Sentiment")
    plt.gcf().autofmt_xdate()
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    #fig, ax = plt.subplot()
    #ax.spines['right'].set_visible(False)
    #ax.spines['top'].set_visible(False)
    #ax.xaxis.set_ticks_position('bottom')
    #ax.yaxis.set_ticks_position('left')
    return plt

def percentage_votes(votes):
    output = {}
    for key in votes.keys():
        output[key] = []
        output[key].append(sum(votes[key]))

    sorted_output = {}
    sorted_output = sorted(output.items(), key = operator.itemgetter(0))

    final_list_y = []
    final_list_y = [item[1] for item in sorted_output]

    return final_list_y


def main(ini_time,tbin, modo,modo2):

    dictionary = {}
    dictionary = analizando()
    plot_output = 0
    total_votes = 0
    nombres_partidos = []
    nombres_partidos.append(['vvd','blue'])
    nombres_partidos.append(['pvv','grey'])
    nombres_partidos.append(['d66','sienna'])
    nombres_partidos.append(['gl', 'yellow'])
    nombres_partidos.append(['cda','green'])
    nombres_partidos.append(['pvda','red'])
    nombres_partidos.append(['sp','pink'])
    nombres_partidos.append(['cu', 'olivedrab'])
    nombres_partidos.append(['50plus','deepskyblue'])
    nombres_partidos.append(['pvdd', 'coral'])
    nombres_partidos.append(['sgp', 'hotpink'])

    ## Compute total votes

    for partido in dictionary.keys():
        votes = {}
        sentimiento = {}
        votes, sentimiento = otro_contador(dictionary,tbin, ini_time, partido)
        vot_part = percentage_votes(votes)
        total_votes += int(vot_part[0][0])

    for partido in dictionary.keys():
        votes = {}
        sentimiento = {}
        votes, sentimiento = otro_contador(dictionary,tbin, ini_time, partido)
        if modo == 1 and modo2 == 'all':
            plt, plot_output = plot_votes(votes, tbin, partido, nombres_partidos, total_votes,modo2)
        else:
            plt, plot_output = plot_votes(votes, tbin, partido, nombres_partidos, 1,modo2)
        if modo == 2:
            plt = plot_sentimientos(sentimiento, tbin,partido,nombres_partidos,modo2)

    if plot_output == 1:
        markes = range(0,len(nombres_partidos))
        labels = []
        for item in nombres_partidos:
            labels.append(item[0])
        plt.xticks(markes, labels)
    else:
        plt.savefig("Exp_more_%s.png" % modo)

    plt.show()

    return total_votes

if __name__ == '__main__':
    main()
