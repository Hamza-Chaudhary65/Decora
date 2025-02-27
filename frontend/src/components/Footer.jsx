import { Link } from 'react-router-dom';
import { FaFacebookF, FaTwitter, FaInstagram } from 'react-icons/fa';

const Footer = () => {
  return (
    <footer className=" py-8">
      <div className="container mx-auto px-4">
        <div className="flex flex-wrap justify-between ">
          <div className="w-full md:w-1/3 mb-4 md:mb-0">
            <h2 className="text-lg font-semibold ">DECORA</h2>
            <p className="text-gray-700  mt-2">Find the perfect furniture for your home.</p>
          </div>
          <div className="w-full md:w-1/3 mb-4 md:mb-0">
            <h3 className="text-lg font-semibold  mb-2">Links</h3>
            <ul>
              <li><Link to="/contactus" className="text-gray-800 hover:text-gray-950 hover:font-semibold">Contact Us</Link></li>
              <li><Link to="/aboutus" className="text-gray-800 hover:text-gray-950 hover:font-semibold">About Us</Link></li>
            </ul>
          </div>
          <div className="w-full md:w-1/3">
            <h3 className="text-lg font-semibold  mb-2">Follow Us</h3>
            <div className="flex items-center">
              <a href="#" className="text-gray-700 hover:text-gray-950 mr-4">
                <FaFacebookF />
              </a>
              <a href="#" className="text-gray-700 hover:text-gray-950 mr-4">
                <FaTwitter />
              </a>
              <a href="#" className="text-gray-700 hover:text-gray-950">
                <FaInstagram />
              </a>
            </div>
          </div>
        </div>
        <div className="border-t border-[#6f3914] mt-8 pt-4">
          <p className="text-center text-gray-700 ">&copy; {new Date().getFullYear()} DECORA. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
