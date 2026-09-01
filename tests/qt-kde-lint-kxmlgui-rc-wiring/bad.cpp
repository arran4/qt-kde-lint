class KXmlGuiWindow {
public:
    void setXMLFile(const char* file) {}
};

void test() {
    KXmlGuiWindow w;
    w.setXMLFile("foo.rc");
}
