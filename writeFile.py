def writeFile(filename, data):
    """Writes 'data' to 'filename'"""
    with open(filename, "w") as f:
        f.write(data)
        f.close()
