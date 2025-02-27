import { useState } from "react";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";


const Hero = () => {

  const [searchQuery, setSearchQuery] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    // Redirect to shop page with search query as URL parameter
    navigate(`/shop?search=${encodeURIComponent(searchQuery)}`);
  };

  const [BannerImg, setBannerImg] = useState({
    one: true,
    two: false,
    three: false,
  });
  const [BannerImgDes, setBannerImgDes] = useState({
    one: false,
    two: false,
    three: false,
  });

  const handerBannerControls = (data) => {
    if (data === "one") {
      setBannerImg({
        one: true,
        two: false,
        three: false,
      });
      setBannerImgDes({
        one: false,
        two: false,
        three: false,
      });
    } else if (data === "two") {
      setBannerImg({
        one: false,
        two: true,
        three: false,
      });
      setBannerImgDes({
        one: false,
        two: false,
        three: false,
      });
    } else if (data === "three") {
      setBannerImg({
        one: false,
        two: false,
        three: true,
      });
      setBannerImgDes({
        one: false,
        two: false,
        three: false,
      });
    }
  };

  const handerBannerControlsdes = (data) => {
    if (data === "one") {
      setBannerImgDes({
        one: true,
        two: false,
        three: false,
      });
    } else if (data === "two") {
      setBannerImgDes({
        one: false,
        two: true,
        three: false,
      });
    } else if (data === "three") {
      setBannerImgDes({
        one: false,
        two: false,
        three: true,
      });
    }
  };

  return (
    <section className="bg-[#d1c7a3] md:h-[85vh] h-auto px-2 md:px-0 ">
      <div className="w-full md:flex md:h-full">
        <div className="md:w-[40%] w-full 5/5 relative md:px-2">
          <div className="md:absolute md:left-[20%] flex py-20 md:py-0 items-center h-full w-full ">
            <div className=" pr-2 pl-1 md:pl-0 md:w-[80%] w-full">
              <h1 className="md:text-7xl text-6xl font-bold leading-tight text-black">
                Future <br /> of furniture
              </h1>
              <p className="my-4 text-gray-500">
              Transform your home with timeless elegance and comfort. 
              iscover our exquisite furniture collection today.
              </p>
              <div className="w-[95%] md:w-full">
                <form className="flex border border-black" onSubmit={handleSubmit}>
                  <input
                    className="flex-1 text-black w-full px-3 bg-transparent focus:outline-none"
                    type="text"
                    name="search"
                    value={searchQuery}
                    placeholder="Search your product here..."
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  <button
                    type="submit"
                    className="bg-black text-white px-7 py-3"
                  >
                    Search
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>

        <div className="md:w-[60%] w-full grow 5/5 md:px-2 h-[50vh] md:h-full">
          <div className="flex gap-3 h-full">
            <div
              onMouseEnter={() => handerBannerControls("one")}
              className={` bg-[url(https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=870&q=80)] bg-center bg-no-repeat bg-cover relative overflow-hidden transition-all duration-500 ease-linear ${
                BannerImg.one ? `w-[60%]` : `w-[20%]`
              }`}
            >
              <div className="absolute">
                <div className="relative">
                  <div className="absolute top-96 left-40">
                    <div className="relative">
                      {BannerImg.one && (
                        <div>
                          <span
                            className="flex h-4 w-4 cursor-pointer"
                            onMouseEnter={() => handerBannerControlsdes("one")}
                          >
                            <span className="animate-ping absolute inline-flex h-full w-full  bg-white opacity-75"></span>
                            <span className="relative inline-flex h-4 w-4 bg-white"></span>
                          </span>
                        </div>
                      )}

                      {BannerImgDes.one ? (
                        <>
                          <div className="absolute bottom-[150%] left-[50%] bg-white px-5 py-2 rounded w-60 shadow">
                            <p className="text-gray-600">
                              <b>Hello!</b>
                            </p>
                            <p>
                              This is a{" "}
                              <Link
                                className="text-black "
                                to="/products/rec7JInsuCEHgmaGe"
                              >
                                Sofa
                              </Link>
                              .
                            </p>
                          </div>
                        </>
                      ) : (
                        ""
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div
              onMouseEnter={() => handerBannerControls("two")}
              className={`bg-[url(https://images.unsplash.com/photo-1524758631624-e2822e304c36?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=870&q=80)] bg-center bg-no-repeat bg-cover relative overflow-hidden transition-all duration-500 ease-linear   ${
                BannerImg.two ? `w-[60%]` : `w-[20%]`
              }`}
            >
              <div className="absolute">
                <div className="relative">
                  <div className="absolute top-96 left-40">
                    <div className="relative">
                      {BannerImg.two && (
                        <div>
                          <span
                            className="flex h-4 w-4 cursor-pointer"
                            onMouseEnter={() => handerBannerControlsdes("two")}
                          >
                            <span className="animate-ping absolute inline-flex h-full w-full  bg-white opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-4 w-4 bg-white"></span>
                          </span>
                        </div>
                      )}

                      {BannerImgDes.two ? (
                        <>
                          <div className="absolute bottom-[150%] left-[50%] bg-white px-5 py-2 rounded w-60 shadow">
                            <p className="text-gray-600">
                              <b>Hello!</b>
                            </p>
                            <p>
                              This is a{" "}
                              <Link
                                className="text-black"
                                to="/products/recd1jIVIEChmiwhe"
                              >
                                Chair
                              </Link>
                              .
                            </p>
                          </div>
                        </>
                      ) : (
                        <></>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div
              onMouseEnter={() => handerBannerControls("three")}
              className={`bg-[url(https://images.unsplash.com/photo-1586023492125-27b2c045efd7?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=958&q=80)] bg-center bg-no-repeat bg-cover relative overflow-hidden transition-all duration-500 ease-linear   ${
                BannerImg.three ? `w-[60%]` : `w-[20%]`
              }`}
            >
              <div className="absolute">
                <div className="relative">
                  <div className="absolute top-96 left-[380px]">
                    <div className="relative">
                      {BannerImg.three && (
                        <div>
                          <span
                            className="flex h-4 w-4 cursor-pointer"
                            onMouseEnter={() =>
                              handerBannerControlsdes("three")
                            }
                          >
                            <span className="animate-ping absolute inline-flex h-full w-full  bg-white opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-4 w-4 bg-white"></span>
                          </span>
                        </div>
                      )}
                      {BannerImgDes.three ? (
                        <>
                          <div className="absolute bottom-[150%] left-[-650%] bg-white px-5 py-2 rounded w-60 shadow">
                            <p className="text-gray-600">
                              <b>Hello!</b>
                            </p>
                            <p>
                              This is a{" "}
                              <Link
                                className="text-black"
                                to="/products/rec3jeKnhInKHJuz2"
                              >
                                {" "}
                                Vase
                              </Link>
                              .
                            </p>
                          </div>
                        </>
                      ) : (
                        <></>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
