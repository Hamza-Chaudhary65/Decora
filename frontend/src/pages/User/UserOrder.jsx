import Message from "../../components/Message";
import Loader from "../../components/Loader";
import { Link } from "react-router-dom";
import { useGetMyOrdersQuery } from "../../redux/api/orderApiSlice";

const UserOrder = () => {
  const { data: orders, isLoading, error } = useGetMyOrdersQuery();

  return (
    <>
      {orders && orders.length === 0 ? (
        <div className="p-5 flex w-full justify-center flex-wrap flex-col">
          <div className="p-5 flex w-full justify-center flex-wrap ">
            <h2 className="text-2xl font-semibold mb-4">Nothing in Orders </h2>
          </div>
          <div className="p-5 flex w-full justify-center flex-wrap ">
            <Link to="/shop">
              <button className="text-white bg-[#645832] hover:bg-[#5c4d1c] py-2 px-3 rounded">
                SHOP ITEMS
              </button>
            </Link>
          </div>
        </div>
      ) : (
        <div className="container mx-auto">
          <h2 className="text-2xl font-semibold mb-4">My Orders </h2>

          {isLoading ? (
            <Loader />
          ) : error ? (
            <Message variant="danger">
              {error?.data?.error || error.error}
            </Message>
          ) : (
            <div className="overflow-x-auto">
            <table className="w-full ">
              <thead>
                <tr>
                  <td className="py-2">IMAGE</td>
                  <td className="py-2">ID</td>
                  <td className="py-2">DATE</td>
                  <td className="py-2">TOTAL</td>
                  <td className="py-2">PAID</td>
                  <td className="py-2">DELIVERED</td>
                  <td className="py-2"></td>
                </tr>
              </thead>

              <tbody>
                {orders.map((order) => (
                  <tr key={order._id}>
                    <img
                      src={order.orderItems[0].image}
                      alt={order.user}
                      className="w-[6rem] mb-5"
                    />

                    <td className="py-2">{order._id}</td>
                    <td className="py-2">{order.createdAt.substring(0, 10)}</td>
                    <td className="py-2">Rs {order.totalPrice}</td>

                    <td className="py-2">
                      {order.isPaid ? (
                        <p className="p-1 text-center text-white bg-green-600 w-[6rem] rounded-full">
                          Completed
                        </p>
                      ) : (
                        <p className="p-1 text-center text-white bg-red-600 w-[6rem] rounded-full">
                          Pending
                        </p>
                      )}
                    </td>

                    <td className="px-2 py-2">
                      {order.isDelivered ? (
                        <p className="p-1 text-center text-white bg-green-600 w-[6rem] rounded-full">
                          Completed
                        </p>
                      ) : (
                        <p className="p-1 text-center bg-red-600 text-white w-[6rem] rounded-full">
                          Pending
                        </p>
                      )}
                    </td>

                    <td className="px-2 py-2">
                      <Link to={`/order/${order._id}`}>
                        <button className="text-white bg-[#645832] hover:bg-[#5c4d1c] py-2 px-3 rounded">
                          View Details
                        </button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          )}
        </div>
      )}
    </>
  );
};

export default UserOrder;
