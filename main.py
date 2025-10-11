from modules import web_search, text_reconstruction, report_generation

fragment = input("Enter the fragmented information: ")
reconstruction = text_reconstruction(fragment)
source = web_search(fragment)
report = report_generation(reconstruction, source)

print(report)