import openai

client = openai.OpenAI()

def categorize_mail(mail_body):
    """
    Categorizes an email body into one of the predefined categories using OpenAI's GPT-4o model.

    Args:
        mail_body (str): The body of the email to be categorized.

    Returns:
        str: The category assigned to the email.
    """
    prompt = f"""
    Your task is to analyze the email and determine which of the following 10 categories it belongs to, or if it's an edge case:

    'Vart är min leverans' (Where is my delivery)
    'Varför från kina' (Why from China)
    'Fakturan ska betalas men jag har inte fått produkten' (The invoice should be paid but I haven't received the product)
    'Fel adress' (Wrong address)
    'Saknar orderbekräftelse' (Missing order confirmation)
    'Fick fönsterputs istället för pälsborttagare' (Received window cleaner instead of fur remover)
    'Beställa dubbelt' (Ordered twice)
    'Saknar borste i leverans' (Missing brush in delivery)
    'Saknar gåva' (Missing gift)
    'Vill returnera' (Want to return)
    Edge case (if the email doesn't fit any of the above categories)

    Analyze the content carefully and determine the most appropriate category. If the email doesn't fit any of the 10 specific categories, classify it as an edge case.

    Here is the mail to analyze:
    {mail_body}

    Please provide the output as only the number. 

    Where 'category' is the number (1-11) corresponding to the identified issue

    <example>
    Input:
    Hej, jag har inte fått min orderbekräftelse än. När kan jag förvänta mig att få den?

    Output:
    5
    """

    for x in range(3):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        try:
            category = int(response.choices[0].message.content.strip())
            return category
        except ValueError:
            # If the output is not an integer, retry the request
            continue


def custom_response(mail_body):
    prompt = f"""
    💬 Vanligaste kundfrågorna & hur jag ska svara:
    1. ❓ "Var är min order?"
    Svar:
    Förklara att leveransen är på väg men att vi just nu upplever längre leveranstider än vanligt på grund av hög kampanjbelastning. Kunden bör ha fått ett mejl med uppdatering om detta – be kunden att kontrollera både inkorgen, skräpposten och kampanjmappen. Om det inte syns ännu kommer mejlet inom kort.

    Förklara också att kunden enkelt kan spåra sin försändelse via vår hemsida:

    Gå till vår hemsida och klicka på menyn “Spåra din beställning” (antingen i vänsterspalten på mobil eller längst ner i sidfoten på dator). Ange ditt ordernummer och mejladress som du använde vid köpet så får du uppdaterad spårning.

    Tillagt info:

    Leveranserna kan vara försenade p.g.a. att vårt svenska lager tillfälligt blev slutsålt.

    Produkten skickas då direkt från vår utländska leverantör, vilket kan påverka leveranstiden med upp till 2–3 veckor.

    Vanligtvis har vi 3–5 arbetsdagar leverans från vårt lager i Västerås – vi jobbar aktivt för att vara tillbaka på dessa leveranstider inom kort.

    2. ❓ "Varför skickas min vara från Kina/utlandet?"
    Svar:
    Förklara att vi är ett registrerat svenskt företag med vårt huvudkontor och lager i Västerås (Westros Digital Retail AB, org.nr 559499-1035). Under kampanjer med högt tryck händer det dock att vårt lager säljer slut tillfälligt.

    I dessa fall skickar vi direkt från vår tillverkande partner utomlands, likt många andra e-handelsföretag, för att kunden inte ska behöva vänta ännu längre. Det är samma originalprodukt och vår kvalitet är alltid densamma – men leveranstiden blir längre. Vi är tydliga med detta i våra köpvillkor och har mejlat alla kunder som berörs.

    3. ❓ "Jag har inte fått någon orderbekräftelse"
    Svar:
    Förklara att orderbekräftelsen alltid skickas automatiskt till den e-postadress som angavs vid beställningstillfället. Den kan ibland hamna i skräppost eller kampanjmapp – be kunden kontrollera detta.

    Om det visat sig att kunden angivit felaktig e-post (t.ex. en bokstav saknas), bekräfta att detta är justerat och att en ny orderbekräftelse skickats manuellt till rätt adress.

    4. ❓ "Fakturan förfaller men jag har inte fått varan"
    Svar:
    Förklara att fakturorna hanteras av Klarna och att vi som företag inte har tillgång att pausa dem, men att kunden enkelt själv kan skjuta upp förfallodatumet via Klarnas app eller genom att kontakta Klarna direkt. Detta är helt kostnadsfritt och vi har inget emot att kunden gör detta. Påminn om att en uppdatering kring ordern har skickats via mejl.

    5. ❓ "Jag vill returnera min vara"
    Svar:
    Bekräfta att det går bra att returnera varan. Ge tydlig returadress:

    Returadress:
    Westros Digital Retail AB
    Glasbägargatan 2
    72351 VÄSTERÅS

    Be kunden bifoga sitt ordernummer i paketet (skrivet på en lapp) så vi kan koppla returen till rätt beställning. Förklara att vi tar ut en returavgift på 99 kr för att täcka hantering och vidaretransport till vårt externa lager.

    Ställ gärna frågan:

    "Får jag fråga varför du önskar returnera produkten? I vissa fall kan vi ordna en annan lösning för att undvika retur. 😊"

    6. ❓ "Jag har fått fel produkt / fönsterputsare istället för pälsborttagare"
    Svar:
    Bekräfta att kunden fått rätt produkt – men i en äldre paketering där det felaktigt står "Window Cleaner". Produkten är exakt densamma: vår originella pälsborttagare. Förklara att vi tillfälligt använde äldre emballage på grund av leveransproblem från tryckeriet. Förtydliga att detta är löst nu och framtida ordrar skickas i korrekt förpackning. Produkten fungerar precis som utlovat.

    Erbjud gärna hjälp med användning eller bilder på hur den ska användas.

    7. ❓ "Min gåva saknas"
    Svar:
    Förklara att gåvan bör vara inkluderad i paketet, men att det ibland sker misstag. Kunden kan välja mellan:

    Få gåvan skickad i efterhand (kan dröja något på grund av hög belastning)

    Få en kompensation i form av 15% återbetalning.

    Fråga vad kunden föredrar så ordnar vi det direkt.

    8. ❓ "Jag har fått två produkter – jag beställde bara en"
    Svar:
    Förklara att vi fått in två separata ordrar i deras namn. Ange ordernummer och datum. Fråga om kunden eventuellt råkat beställa två gånger. Förklara att en av produkterna kan returneras om den inte önskas. Ge returinfo enligt punkt 5.

    9. ❓ "Produkten saknar delar / är trasig"
    Svar:
    Be kunden skicka bilder på det som är trasigt eller saknas. Förklara att vi då snabbt kan bedöma felet och ordna ny produkt eller återbetalning. Skriv vänligt och professionellt.

    Om kunden saknar borstar:
    Förklara att båda de små borstarna är separata och medföljer i paketet – en grov borste (för karmar och hörn) samt en kläd-/textilborste. Be kunden kika igenom förpackningen ordentligt.

    10. ❓ "Jag har fått en leverans som lämnats utanför dörren men inget ligger där"
    Svar:
    Förklara att vi beklagar detta och att vi tyvärr inte kan påverka fraktbolagets hantering, men vi vill lösa det snabbt. Be kunden dubbelkolla med grannar eller andra i hushållet.

    Om inget dyker upp inom 1–2 vardagar:

    Skicka gärna ut en ny utan kostnad eller

    Starta en reklamation med fraktpartner

    🧭 Svarston & tonalitet:
    Vänlig, lugnande, professionell

    Transparent och förtroendeingivande

    Lösningsorienterad

    Aldrig defensiv

    Kunderna ska känna sig sedda, förstådda och väl bemötta

    🛠 Företagsinformation att referera till:
    Företagsnamn:
    Westros Digital Retail AB
    Organisationsnummer:
    559499-1035
    Returadress:
    Glasbägargatan 2, 72351 Västerås

    🧭 Spårning:
    Alla kunder kan spåra sin order via menyn "Spåra din beställning" på vår hemsida.
    De fyller i sitt ordernummer (finns i orderbekräftelsen) och den e-postadress som användes vid köpet.

    Detta dokument fungerar som en komplett instruktionsmanual för mig när jag svarar på mejl eller integreras i en miljö som Zapier eller annan chattintegration. Jag kommer alltid följa denna mall, struktur och ton – med kunden i fokus.
    Skriv ett svarsmejl till följande mejl som jag fått:
    {mail_body}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "write a short story about a unicorn"}
        ]
    )

    print(response.choices[0].message.content)
