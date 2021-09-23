import records.record as record


def parseAuthorityRecords(response):
    authorityRecords = response.authority[0].to_text()
    uncleanedAuths = authorityRecords.split("\n")
    auths = []
    for a in uncleanedAuths:
        auths.append(record.parse(a))
    return auths


def parseAnswers(response):
    answerRecords = response.answer[0].to_text()
    uncleanedRecords = answerRecords.split("\n")
    answers = []
    for a in uncleanedRecords:
        answers.append(record.parse(a))
    return answers


def parseAdditionalRecords(response):
    additionalRecords = []
    for add in response.additional:
        addRecord = record.parse(add.to_text())
        additionalRecords.append(addRecord)
    return additionalRecords
