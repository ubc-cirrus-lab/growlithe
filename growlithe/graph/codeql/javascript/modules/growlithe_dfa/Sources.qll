import javascript
import DataFlow
import modules.growlithe_dfa.Core
import modules.growlithe_dfa.Utils

module Sources {
  class ParameterSource extends Core::Source {
    Function f;

    ParameterSource() {
      this instanceof DataFlow::ParameterNode and
      f.getName() = "handler" and
      this = f.getAParameter().flow()
    }

    override string getObjectPath() { result = Utils::strRepr(this) }

    override Utils::ShareType getShareType() { result = "INVOCATION" }

    override string getResource() { result = "PARAM:STATIC:SourceCode" }
  }

  class AxiosRequest extends Core::Source {
    ClientRequest::AxiosUrlRequest axiosUrlRequest;

    AxiosRequest() { this = axiosUrlRequest }

    override string getResource() { result = axiosUrlRequest.getUrl().toString() }

    override Utils::ShareType getShareType() { result = "GLOBAL" }

    override string getObjectPath() { result = Utils::strRepr(this) }
  }
}
