import nest_asyncio

nest_asyncio.apply()
from langchain_community.document_loaders.sitemap import SitemapLoader

sitemap_loader = SitemapLoader(web_path="https://api.python.langchain.com/sitemap.xml")

docs = sitemap_loader.load()

for doc in docs:
    print(doc.metadata)
    print(doc.page_content)
    print("===" * 20)